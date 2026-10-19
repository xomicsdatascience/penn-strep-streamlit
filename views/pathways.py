import streamlit as st
import plotly.express as px
import pandas as pd
import os
from config import PLOTLY_TEMPLATE
from utils.data_loader import load_pathways_data

def show():
    st.markdown("## 🧬 Pathway Enrichment & Gene Ontology (GO)")
    st.markdown("""
    Explore **Figure 4** and **Figures S13–S14**: biological pathways and gene ontology terms 
    significantly enriched among proteins altered by penicillin-streptomycin exposure.
    """)
    
    pathways_df = load_pathways_data()
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Interactive Pathway Signatures (Fig 4)",
        "🖼️ Publication Figures (Fig 4, S13, S14)",
        "📋 Full Enriched Pathways Table"
    ])
    
    with tab1:
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            dir_choice = st.selectbox(
                "Filter by Direction:",
                ["All Pathways", "Upregulated without Antibiotics (N/AN)", "Upregulated with Antibiotics (A/NA)"]
            )
        with c_filter2:
            db_list = ["All Databases"] + sorted(pathways_df['Database'].unique().tolist())
            db_choice = st.selectbox("Filter by Annotation Database:", db_list)
            
        plot_df = pathways_df.copy()
        if dir_choice != "All Pathways":
            plot_df = plot_df[plot_df['Direction'] == dir_choice]
        if db_choice != "All Databases":
            plot_df = plot_df[plot_df['Database'] == db_choice]
            
        st.markdown(f"#### Enriched Biological Terms ({len(plot_df)} Pathways)")
        
        # Color based on direction
        color_map = {
            "Upregulated without Antibiotics (N/AN)": "#1976D2",
            "Upregulated with Antibiotics (A/NA)": "#D32F2F"
        }
        
        fig_bar = px.bar(
            plot_df.sort_values('Combined_Score', ascending=True),
            x='Combined_Score',
            y='Term',
            color='Direction',
            color_discrete_map=color_map,
            orientation='h',
            hover_data={
                'Database': True,
                'Adjusted_Pval': ':.2e',
                'Proteins': True,
                'Combined_Score': ':.1f'
            },
            template=PLOTLY_TEMPLATE,
            height=max(400, len(plot_df) * 35)
        )
        fig_bar.update_layout(
            xaxis_title="Enrichment Combined Score",
            yaxis_title="Enriched Pathway / GO Term",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("#### 🔬 Inspect Proteins in a Selected Pathway:")
        path_select = st.selectbox("Choose a Pathway to Inspect Associated Proteins:", plot_df['Term'].tolist())
        if path_select:
            selected_row = plot_df[plot_df['Term'] == path_select].iloc[0]
            st.markdown(f"""
            - **Database:** `{selected_row['Database']}`
            - **Direction:** `{selected_row['Direction']}`
            - **Combined Score:** `{selected_row['Combined_Score']:.1f}` | **Adjusted P-value:** `{selected_row['Adjusted_Pval']:.2e}`
            - **Key Member Proteins:** `{selected_row['Proteins']}`
            """)
            
            # Buttons to jump to trajectory
            prots = [p.strip() for p in selected_row['Proteins'].split(',') if p.strip()]
            st.markdown("**Click a protein to explore in Trajectory view:**")
            p_cols = st.columns(min(len(prots), 6))
            for i, p in enumerate(prots[:6]):
                if p_cols[i].button(p, key=f"path_{p}"):
                    st.session_state['selected_protein'] = p
                    st.success(f"Selected {p}! Switch to '📈 Longitudinal Trajectory Explorer' page to view.")

    with tab2:
        st.markdown("### Publication Figures: Pathway Enrichment")
        fig4_path = "assets/figures/fig4_pathway_enrichment.png"
        if os.path.exists(fig4_path):
            st.image(fig4_path, caption="Figure 4: GO terms upregulated in samples (a) without antibiotics (N) and (b) with antibiotics (A).", use_container_width=True)
            
        with st.expander("🖼️ View Unfiltered Enrichment Results (Figures S13 & S14)"):
            c_s13, c_s14 = st.columns(2)
            with c_s13:
                s13_path = "assets/figures/figS13_go_unfiltered_up_in_N.png"
                if os.path.exists(s13_path):
                    st.image(s13_path, caption="Figure S13: Full unfiltered GO term enrichment results upregulated in N.", use_container_width=True)
            with c_s14:
                s14_path = "assets/figures/figS14_go_unfiltered_up_in_A.png"
                if os.path.exists(s14_path):
                    st.image(s14_path, caption="Figure S14: Full unfiltered GO term enrichment results upregulated in A.", use_container_width=True)

    with tab3:
        st.markdown("### Full Pathway Enrichment Data Table")
        st.dataframe(pathways_df, use_container_width=True)
