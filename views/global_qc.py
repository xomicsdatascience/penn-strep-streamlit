import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from config import CONDITION_COLORS, PLOTLY_TEMPLATE
from utils.data_loader import (
    load_metadata,
    load_expression_data,
    load_pca_data,
    load_blanks_and_qcs
)
from utils.plot_helpers import (
    create_pca_scatter,
    create_detection_histogram,
    create_ranked_abundance_plot
)

def show():
    st.markdown("## 📊 Global Proteome Quantification & Quality Control")
    st.markdown("""
    Explore **Figure 2** and **Figures S1–S2**: global protein abundance distributions, identification depth, 
    detection consistency, and principal component analysis (PCA).
    """)
    
    metadata = load_metadata()
    df_expr = load_expression_data(log2=True, filtered=False)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Abundance & Depth (Fig 2a,b)",
        "🎯 Detection Frequency (Fig 2c)",
        "🏆 Ranked Abundance (Fig 2d)",
        "🌐 PCA & Confluency (Fig S1-S2)",
        "🧪 Blanks & QC Stability (Fig S1f-h)"
    ])
    
    with tab1:
        st.markdown("### Figure 2a & 2b: Protein Quantities and Identification Depth")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Sample Intensity Distributions")
            # Select subset of samples to view or summarize
            cond_select = st.multiselect("Filter by Condition:", ['A', 'N', 'AN', 'NA'], default=['A', 'N', 'AN', 'NA'])
            filtered_meta = metadata[metadata['condition'].isin(cond_select)]
            
            # Plot boxplot of total protein / distribution per condition
            fig_box = px.box(
                filtered_meta,
                x='condition',
                y='total_raw_intensity',
                color='condition',
                color_discrete_map=CONDITION_COLORS,
                points="all",
                hover_name='sample_id',
                labels={'total_raw_intensity': 'Total Summed Intensity', 'condition': 'Condition'},
                template=PLOTLY_TEMPLATE
            )
            fig_box.update_layout(title="Total Protein Intensity by Condition", showlegend=False, height=420)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with c2:
            st.markdown("#### Figure 2b: Detected Proteins per Sample")
            fig_hist = create_detection_histogram(filtered_meta)
            st.plotly_chart(fig_hist, use_container_width=True)
            
        st.info("💡 **Key Finding:** On average, **9,374 proteins** were detected per sample with consistent total protein content across conditions and plates, confirming uniform cell recovery and high reproducibility.")

    with tab2:
        st.markdown("### Figure 2c: Protein Detection Consistency Across 119 Samples")
        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            # Frequency distribution of detection count
            detection_counts = (df_expr.notna() & (df_expr > 0)).sum(axis=1)
            hist_df = pd.DataFrame({'samples_detected': detection_counts.values})
            
            fig_det = px.histogram(
                hist_df,
                x='samples_detected',
                nbins=30,
                color_discrete_sequence=['#1E88E5'],
                labels={'samples_detected': 'Number of Samples (Max 119)'},
                template=PLOTLY_TEMPLATE,
                height=420
            )
            fig_det.update_layout(
                title="Figure 2c: Number of Samples in Which Each Protein Was Detected",
                yaxis_title="Protein Count",
                xaxis=dict(range=[0, 122])
            )
            st.plotly_chart(fig_det, use_container_width=True)
            
        with c2:
            st.markdown("#### Core Proteome Coverage")
            n_total = len(df_expr)
            n_all = (detection_counts == 119).sum()
            n_50pct = (detection_counts >= 60).sum()
            
            st.metric("Total Unique Proteins Detected", f"{n_total:,}")
            st.metric("Detected in 100% of Samples (119/119)", f"{n_all:,} ({n_all/n_total*100:.1f}%)")
            st.metric("Detected in ≥50% of Samples", f"{n_50pct:,} ({n_50pct/n_total*100:.1f}%)")
            
            # Pie / Donut Chart
            pie_data = pd.DataFrame({
                'Category': ['Detected in All 119 Samples', 'Detected in 50–99% Samples', 'Detected in <50% Samples'],
                'Count': [n_all, n_50pct - n_all, n_total - n_50pct]
            })
            fig_pie = px.pie(
                pie_data,
                names='Category',
                values='Count',
                hole=0.45,
                color_discrete_sequence=['#43A047', '#1E88E5', '#FFA000'],
                template=PLOTLY_TEMPLATE,
                height=280
            )
            fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        st.markdown("### Figure 2d: Ranked Mean Protein Abundance")
        st.markdown("Ranked dynamic range spanning over 4 orders of magnitude from highest to lowest abundant proteins.")
        
        df_rank = load_expression_data(log2=True, filtered=True)
        
        # Interactive ranked abundance matching Cell 37 and Figure 2d
        fig_rank = create_ranked_abundance_plot(df_rank)
        st.plotly_chart(fig_rank, use_container_width=True)
        
        # Inset: Top most abundant proteins
        st.markdown("#### Inset: Top Most Abundant Proteins")
        top_n = st.slider("Select Number of Top Proteins to Display:", min_value=5, max_value=25, value=8)
        
        row_means = df_rank.mean(axis=1)
        row_stds = df_rank.std(axis=1)
        
        stats_df = pd.DataFrame({
            'Protein': df_rank.index,
            'Mean_Log2_Intensity': row_means.values,
            'Std_Dev': row_stds.values
        })
        
        # Take the top_n most abundant, ensuring unique proteins
        top_stats = stats_df.sort_values('Mean_Log2_Intensity', ascending=False).drop_duplicates(subset=['Protein']).head(top_n).reset_index(drop=True)
        
        fig_top = px.bar(
            top_stats,
            x='Mean_Log2_Intensity',
            y='Protein',
            orientation='h',
            error_x='Std_Dev',
            color='Mean_Log2_Intensity',
            color_continuous_scale='Plasma',
            template=PLOTLY_TEMPLATE,
            height=380
        )
        fig_top.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Mean Log₂ Abundance (± SD)",
            yaxis_title="Protein",
            title=f"Top {top_n} Most Abundant HepG2 Proteins"
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with tab4:
        st.markdown("### Figures S1 & S2: Principal Component Analysis (PCA)")
        st.markdown("""
        PCA reveals the principal sources of variance across the 119 samples.
        Passages 5 and 6 grouped slightly along PC1 due to transient sub-confluent culture stages, 
        driven by cell cycle / proliferation markers (G2-M checkpoint and E2F targets), which normalizes by passage 7.
        """)
        
        pca_samples, pca_loadings, exp_var = load_pca_data()
        
        c1, c2 = st.columns([0.3, 0.7])
        with c1:
            st.markdown("#### PCA Display Options")
            color_choice = st.radio("Color Samples By:", ['condition', 'passage', 'plate'], index=0)
            st.markdown(f"""
            - **PC1 Explained Variance:** {exp_var[0]*100:.1f}%
            - **PC2 Explained Variance:** {exp_var[1]*100:.1f}%
            - **PC3 Explained Variance:** {exp_var[2]*100:.1f}%
            """)
            
        with c2:
            fig_pca = create_pca_scatter(pca_samples, color_by=color_choice, exp_var=exp_var)
            st.plotly_chart(fig_pca, use_container_width=True)
            
        st.markdown("#### Top PC1 Loadings (Cell Cycle & Metabolic Markers)")
        c_load1, c_load2 = st.columns(2)
        with c_load1:
            st.markdown("**Top Positive Loadings (Associated with Passages 5 & 6):**")
            top_pos = pca_loadings['PC1'].sort_values(ascending=False).head(8).reset_index()
            top_pos.columns = ['Protein', 'PC1 Loading']
            st.dataframe(top_pos, hide_index=True, use_container_width=True)
        with c_load2:
            st.markdown("**Top Negative Loadings:**")
            top_neg = pca_loadings['PC1'].sort_values(ascending=True).head(8).reset_index()
            top_neg.columns = ['Protein', 'PC1 Loading']
            st.dataframe(top_neg, hide_index=True, use_container_width=True)

    with tab5:
        st.markdown("### Figures S1f–h: Quality Controls & Injection Order Stability")
        df_blanks = load_blanks_and_qcs()
        
        qc_cols = [c for c in df_blanks.columns if 'R' in c]
        blank_cols = [c for c in df_blanks.columns if 'blank' in c or 'BKF' in c]
        
        st.markdown(f"Demonstrating instrument stability and lack of carryover across **{len(qc_cols)} pooled QC replicates** and **{len(blank_cols)} solvent/KF blanks**.")
        
        # QC summary metrics
        qc_totals = df_blanks[qc_cols].sum(axis=0)
        cv = (qc_totals.std() / qc_totals.mean()) * 100
        
        col_qc1, col_qc2 = st.columns(2)
        with col_qc1:
            st.metric("Pooled QC Signal CV (%)", f"{cv:.2f}%", help="Coefficient of variation across injection sequence")
        with col_qc2:
            blank_signal_ratio = (df_blanks[blank_cols].sum(axis=0).mean() / qc_totals.mean()) * 100
            st.metric("Blank Background / QC Signal", f"{blank_signal_ratio:.2f}%", help="Near-zero carryover")
            
        qc_df = pd.DataFrame({'QC_Run': range(1, len(qc_totals) + 1), 'Total_Intensity': qc_totals.values})
        fig_qc = px.line(
            qc_df,
            x='QC_Run',
            y='Total_Intensity',
            markers=True,
            title="Pooled Quality Control (QC) Intensity Stability Across Orbitrap Astral Runs",
            labels={'QC_Run': 'QC Injection Sequence (~every 9 samples)', 'Total_Intensity': 'Total Protein Intensity'},
            template=PLOTLY_TEMPLATE,
            height=380
        )
        st.plotly_chart(fig_qc, use_container_width=True)
