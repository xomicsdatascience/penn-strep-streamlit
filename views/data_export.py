import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import (
    load_expression_data,
    load_metadata,
    load_lme_data
)

def show():
    st.markdown("## 🔍 Data Browser & Export")
    st.markdown("""
    Search, filter, and export the complete proteomic quantification matrix and linear mixed effects model results.
    """)
    
    meta = load_metadata()
    df_expr = load_expression_data(log2=True, filtered=False)
    lme_all = load_lme_data()
    
    tab_matrix, tab_lme, tab_meta = st.tabs([
        "📊 Protein Expression Matrix (10,255 Proteins)",
        "🌋 Linear Model Statistics (All Comparisons)",
        "📋 Sample Metadata (119 Samples)"
    ])
    
    with tab_matrix:
        st.markdown("### Search & Filter Protein Expression Matrix")
        
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            gene_query = st.text_input("Search Gene Symbols (e.g. GCAT, CPT1A, MAT2A):", "")
        with c2:
            min_samples = st.slider("Min Samples Detected (out of 119):", 0, 119, 60)
        with c3:
            sig_only = st.checkbox("Show Only Significantly Altered (FDR ≤ 0.01 in any comparison)", value=False)
            
        # Compute summary stats across samples
        det_count = df_expr.notna().sum(axis=1)
        mean_all = df_expr.mean(axis=1)
        
        # Calculate condition means
        cond_means = {}
        for c in ['A', 'N', 'AN', 'NA']:
            c_samples = meta[meta['condition'] == c].index
            cond_means[f'Mean_{c}'] = df_expr[c_samples].mean(axis=1)
            
        summary_df = pd.DataFrame({
            'Samples_Detected': det_count,
            'Detection_Pct': (det_count / len(meta.columns) * 100).round(1),
            'Mean_Log2_Overall': mean_all.round(2),
            'Mean_A': cond_means['Mean_A'].round(2),
            'Mean_N': cond_means['Mean_N'].round(2),
            'Mean_AN': cond_means['Mean_AN'].round(2),
            'Mean_NA': cond_means['Mean_NA'].round(2)
        })
        
        # Filter
        filtered_index = summary_df.index
        if min_samples > 0:
            filtered_index = filtered_index[summary_df['Samples_Detected'] >= min_samples]
            
        if gene_query:
            filtered_index = [idx for idx in filtered_index if gene_query.upper() in str(idx).upper()]
            
        if sig_only:
            sig_proteins = lme_all[lme_all['pval_corrected'] <= 0.01]['protein'].unique()
            filtered_index = [idx for idx in filtered_index if idx in sig_proteins]
            
        st.markdown(f"**Showing {len(filtered_index):,} proteins matching criteria:**")
        display_df = summary_df.loc[filtered_index]
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Export button
        csv_data = df_expr.loc[filtered_index].to_csv().encode('utf-8')
        st.download_button(
            label=f"📥 Download Filtered Expression Matrix (CSV, {len(filtered_index)} proteins)",
            data=csv_data,
            file_name="hepg2_penstrep_filtered_expression_matrix.csv",
            mime="text/csv"
        )

    with tab_lme:
        st.markdown("### Linear Mixed Effects Model Statistics (FC_RI)")
        
        comp_filter = st.selectbox("Filter by Comparison:", ["All Comparisons", "NvA", "NAvA", "ANvA"])
        fdr_filter = st.select_slider("FDR Filter:", options=[0.001, 0.01, 0.05, 0.10, 1.0], value=1.0)
        
        lme_view = lme_all.copy()
        if comp_filter != "All Comparisons":
            lme_view = lme_view[lme_view['comparison'] == comp_filter]
        if fdr_filter < 1.0:
            lme_view = lme_view[lme_view['pval_corrected'] <= fdr_filter]
            
        st.markdown(f"**Showing {len(lme_view):,} entries:**")
        st.dataframe(
            lme_view[['comparison', 'protein', 'coef', 'pval_corrected', '-log10_pval', 'significant_up', 'significant_down']].style.format({
                'coef': '{:.4f}',
                'pval_corrected': '{:.2e}',
                '-log10_pval': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )
        
        csv_lme = lme_view.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download LME Statistics (CSV)",
            data=csv_lme,
            file_name="hepg2_penstrep_lme_statistics.csv",
            mime="text/csv"
        )

    with tab_meta:
        st.markdown("### Sample Metadata (119 Samples)")
        st.dataframe(meta, use_container_width=True, height=400)
        
        csv_meta = meta.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Sample Metadata (CSV)",
            data=csv_meta,
            file_name="hepg2_penstrep_sample_metadata.csv",
            mime="text/csv"
        )
