import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from config import PLOTLY_TEMPLATE
from utils.data_loader import load_lme_data, load_core14_proteins
from utils.plot_helpers import create_volcano_plot

def show():
    st.markdown("## 🌋 Linear Mixed Effects (LME) Modeling & Differential Abundance")
    st.markdown("""
    Explore **Figure 3**: differential protein abundance across conditions using linear mixed effects models (FC_RI).
    - **Fixed Effect:** Treatment Condition (relative to reference **A: Always Antibiotics**)
    - **Random Effect:** Passage (accounting for longitudinal passage-by-passage variation)
    """)
    
    tab_volcano, tab_core14, tab_model_compare = st.tabs([
        "🌋 Interactive Volcano Plots (Fig 3e–g)",
        "⭐ The 14 Core Consistently Altered Proteins (Fig 3h)",
        "📐 Model Selection & Diagnostics (Fig 3a–d, S10)"
    ])
    
    with tab_volcano:
        st.markdown("### Figure 3e–g: Volcano Plots for Each Condition Comparison")
        
        col_comp, col_fdr, col_coef = st.columns([1.2, 1, 1])
        with col_comp:
            comp_choice = st.selectbox(
                "Select Comparison Group (vs Reference A):",
                [
                    ("NvA", "NvA: Always No Antibiotics vs Always Antibiotics (Fig 3e)"),
                    ("NAvA", "NAvA: Crossover N→A vs Always Antibiotics (Fig 3f)"),
                    ("ANvA", "ANvA: Crossover A→N vs Always Antibiotics (Fig 3g)")
                ],
                format_func=lambda x: x[1]
            )[0]
            
        with col_fdr:
            fdr_cutoff = st.select_slider(
                "FDR Cutoff (Benjamini-Hochberg):",
                options=[0.001, 0.01, 0.05, 0.10],
                value=0.01
            )
            
        with col_coef:
            coef_cutoff = st.number_input(
                "Min |Effect Size| (|Coefficient|):",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.05
            )
            
        df_lme = load_lme_data(comparison=comp_choice)
        
        # Highlight gene search
        protein_list = ["None"] + sorted(df_lme['protein'].dropna().unique().tolist())
        highlight_gene = st.selectbox("Highlight Specific Protein on Volcano Plot:", protein_list, index=0)
        highlight_gene = None if highlight_gene == "None" else highlight_gene
        
        # Summary counts
        n_up = ((df_lme['pval_corrected'] <= fdr_cutoff) & (df_lme['coef'] > coef_cutoff)).sum()
        n_down = ((df_lme['pval_corrected'] <= fdr_cutoff) & (df_lme['coef'] < -coef_cutoff)).sum()
        n_sig = n_up + n_down
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Tested Proteins", f"{len(df_lme):,}")
        with m2:
            st.metric("Significantly Altered", f"{n_sig:,}", delta=f"{n_sig/len(df_lme)*100:.2f}%")
        with m3:
            st.metric("Higher in Condition (Up)", f"{n_up:,}", delta_color="normal")
        with m4:
            st.metric("Higher in Antibiotics A (Down)", f"{n_down:,}", delta_color="inverse")
            
        # Title of the comparison
        titles = {
            "NvA": "Figure 3e: N vs A (No Antibiotics vs Antibiotics)",
            "NAvA": "Figure 3f: NA vs A (Crossover into Antibiotics vs Continual Antibiotics)",
            "ANvA": "Figure 3g: AN vs A (Crossover out of Antibiotics vs Continual Antibiotics)"
        }
        fig_volc = create_volcano_plot(
            df_lme,
            fdr_cutoff=fdr_cutoff,
            coef_cutoff=coef_cutoff,
            highlight_gene=highlight_gene,
            title=titles.get(comp_choice, "Volcano Plot")
        )
        st.plotly_chart(fig_volc, use_container_width=True)
        
        # Filtered table of significant proteins
        st.markdown(f"#### Significant Proteins in {comp_choice} (FDR ≤ {fdr_cutoff}, |coef| ≥ {coef_cutoff})")
        sig_df = df_lme[
            (df_lme['pval_corrected'] <= fdr_cutoff) & 
            (df_lme['coef'].abs() >= coef_cutoff)
        ].sort_values('pval_corrected')
        
        display_cols = ['protein', 'coef', 'pval_corrected', '-log10_pval']
        st.dataframe(
            sig_df[display_cols].style.format({
                'coef': '{:.3f}',
                'pval_corrected': '{:.2e}',
                '-log10_pval': '{:.2f}'
            }),
            use_container_width=True,
            height=300
        )
        
        # Download button
        csv = sig_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {comp_choice} Significant Proteins (CSV)",
            data=csv,
            file_name=f"pen_strep_lme_{comp_choice}_sig_p_{fdr_cutoff}.csv",
            mime="text/csv"
        )

    with tab_core14:
        st.markdown("### Figure 3h: The 14 Core Consistently Altered Proteins")
        st.markdown("""
        Benefiting from the longitudinal crossover design, **14 proteins were consistently differentially abundant 
        across multiple comparisons** (both N vs A and AN vs A):
        - **4 proteins** consistently elevated in **Non-Antibiotic conditions** (N, AN).
        - **10 proteins** consistently elevated in **Antibiotic conditions** (A).
        """)
        
        core14 = load_core14_proteins()
        
        col_up, col_down = st.columns(2)
        with col_up:
            st.markdown("#### 🔵 Increased in Non-Antibiotics (N & AN)")
            up_core = core14[core14['direction'].str.contains("Non-Antibiotics")]
            for _, r in up_core.iterrows():
                with st.expander(f"**{r['protein']}** - {r['name']}"):
                    st.markdown(f"**Localization:** {r['localization']}")
                    st.markdown(f"**NvA Effect:** coef = `{r['NvA_coef']:+.3f}` (p = `{r['NvA_pval']:.2e}`)")
                    st.markdown(f"**ANvA Effect:** coef = `{r['ANvA_coef']:+.3f}` (p = `{r['ANvA_pval']:.2e}`)")
                    st.markdown(f"**Function:** {r['function']}")
                    
        with col_down:
            st.markdown("#### 🔴 Increased in Antibiotics (A)")
            down_core = core14[core14['direction'].str.contains("Antibiotics \(A\)")]
            for _, r in down_core.iterrows():
                with st.expander(f"**{r['protein']}** - {r['name']}"):
                    st.markdown(f"**Localization:** {r['localization']}")
                    st.markdown(f"**NvA Effect:** coef = `{r['NvA_coef']:+.3f}` (p = `{r['NvA_pval']:.2e}`)")
                    st.markdown(f"**ANvA Effect:** coef = `{r['ANvA_coef']:+.3f}` (p = `{r['ANvA_pval']:.2e}`)")
                    st.markdown(f"**Function:** {r['function']}")
                    
        st.dataframe(core14[['protein', 'name', 'localization', 'direction', 'NvA_coef', 'NvA_pval', 'ANvA_coef', 'ANvA_pval']], use_container_width=True)

    with tab_model_compare:
        st.markdown("### Linear Mixed Effects Model Selection & Diagnostics (Figures 3a–d, S10)")
        st.markdown("""
        To avoid confounding biological changes with passage-dependent drift, 8 candidate models were compared:
        - **Ordinary Least Squares (OLS):** Condition only (C), Condition + Passage (C_P), Condition × Passage interaction (CxP).
        - **Linear Mixed Models (LME):**
          - Random Intercept (RI): Passage as random effect.
          - Random Intercept + Slope (RI_RS).
          - Fixed Condition + Random Intercept (**FC_RI**, the selected model, lowest AIC).
          - Fixed Condition + Random Intercept & Slope (FC_RI_RS).
        """)
        
        fig3_path = "assets/figures/fig3_lme_volcano_euler.png"
        if os.path.exists(fig3_path):
            st.image(fig3_path, caption="Figure 3: Linear mixed effect modeling workflow, model selection, random intercepts, fixed effects, volcano plots, and Venn diagram of altered proteins.", use_container_width=True)
            
        st.info("""
        🔬 **Random Intercept Interpretation (Fig 3c):**
        Passage-by-passage variation was greatest immediately following treatment crossover (Passages 1 and 6), 
        and stabilized after ~3 passages (Passages 3 and 8). This confirms that cells require at least **three passages (~9-10 days)** 
        to acclimate and stabilize their proteomic phenotype when transitioning into or out of antibiotic media.
        """)
