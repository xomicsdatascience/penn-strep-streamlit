import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import CONDITION_COLORS, CONDITION_LABELS, PLOTLY_TEMPLATE
from utils.data_loader import (
    load_metadata,
    load_expression_data,
    load_lme_data,
    get_protein_trajectory
)
from utils.plot_helpers import create_trajectory_plot

def show():
    st.markdown("## 📈 Longitudinal Protein Trajectory Explorer")
    st.markdown("""
    Explore how protein expression evolves across **Passages 1 through 9** under continual vs crossover antibiotic treatment.
    Inspect the dynamic adaptation of any of the **10,255 quantified proteins**.
    """)
    
    metadata = load_metadata()
    df_expr = load_expression_data(log2=True, filtered=False)
    lme_all = load_lme_data()
    
    # Quick pick buttons for prominent proteins
    st.markdown("#### Quick-Pick Prominent Proteins from the Paper:")
    quick_picks = [
        "GCAT", "CPT1A", "MAT2A", "PDIA2", "FAM3C", "MTDH", 
        "CTSC", "HEXB", "STEAP3", "GPX2", "ACSL3", "PKLR"
    ]
    
    cols = st.columns(len(quick_picks))
    selected_quick = None
    for i, p in enumerate(quick_picks):
        if cols[i].button(p, use_container_width=True):
            st.session_state['selected_protein'] = p
            
    # Search / dropdown input
    all_proteins = sorted(df_expr.index.unique().tolist())
    
    current_default = st.session_state.get('selected_protein', 'GCAT')
    if current_default not in all_proteins:
        current_default = all_proteins[0]
        
    selected_prot = st.selectbox(
        "Search or Select a Protein Symbol:",
        all_proteins,
        index=all_proteins.index(current_default)
    )
    
    st.session_state['selected_protein'] = selected_prot
    
    # Generate trajectory dataframe
    df_traj = get_protein_trajectory(selected_prot, df_expr=df_expr, metadata=metadata)
    
    if df_traj is None:
        st.warning(f"Protein {selected_prot} not found in the dataset.")
        return
        
    # Get LME stats for this protein
    prot_lme = lme_all[lme_all['protein'] == selected_prot]
    
    c1, c2, c3 = st.columns(3)
    for comp, col in zip(['NvA', 'NAvA', 'ANvA'], [c1, c2, c3]):
        sub_lme = prot_lme[prot_lme['comparison'] == comp]
        with col:
            if not sub_lme.empty:
                r = sub_lme.iloc[0]
                sig_str = "⭐ Significant" if r['pval_corrected'] <= 0.01 else ("Significant (p≤0.1)" if r['pval_corrected'] <= 0.1 else "Not Significant")
                st.metric(
                    label=f"LME: {comp}",
                    value=f"coef = {r['coef']:+.3f}",
                    delta=f"adj. p = {r['pval_corrected']:.2e} ({sig_str})",
                    delta_color="normal" if r['pval_corrected'] <= 0.01 else "off"
                )
            else:
                st.metric(label=f"LME: {comp}", value="N/A")
                
    # Trajectory Plot
    fig_traj = create_trajectory_plot(df_traj, selected_prot)
    st.plotly_chart(fig_traj, use_container_width=True)
    
    # Interpretation note on crossover behavior
    st.markdown("""
    ##### 🔍 How to Interpret the Crossover Trajectories:
    - **A (Red, Passages 1–9):** Steady-state in PenStrep media.
    - **N (Blue, Passages 1–9):** Steady-state without PenStrep media.
    - **AN (Orange, Passages 6–9):** Grown with antibiotics in P1–5, then antibiotics were **withdrawn** at P5. Observe whether abundance shifts towards the blue (N) baseline!
    - **NA (Teal, Passages 6–9):** Grown without antibiotics in P1–5, then antibiotics were **initiated** at P5. Observe whether abundance shifts towards the red (A) baseline!
    """)
    
    with st.expander("📊 View Raw Expression Values for this Protein"):
        pivot_df = df_traj.pivot_table(index='passage', columns='condition', values='expression', aggfunc=['mean', 'std'])
        st.dataframe(pivot_df, use_container_width=True)
        
    st.divider()
    
    # Multi-Protein Comparison Mode
    st.markdown("### 🔀 Multi-Protein Overlay Comparison")
    st.markdown("Compare longitudinal trajectories of 2 to 5 proteins simultaneously:")
    
    multi_select = st.multiselect(
        "Select Proteins to Compare:",
        all_proteins,
        default=["GCAT", "MAT2A", "CPT1A"]
    )
    
    if multi_select:
        fig_multi = go.Figure()
        colors = ['#1976D2', '#D32F2F', '#388E3C', '#F57C00', '#7B1FA2']
        
        for idx, p_sym in enumerate(multi_select):
            traj = get_protein_trajectory(p_sym, df_expr=df_expr, metadata=metadata)
            if traj is not None:
                # Group by passage and condition or overall condition
                p_col = colors[idx % len(colors)]
                # Show A vs N lines for each protein
                for cond in ['A', 'N']:
                    sub = traj[traj['condition'] == cond].groupby('passage')['expression'].mean().reset_index()
                    line_style = 'solid' if cond == 'N' else 'dash'
                    fig_multi.add_trace(go.Scatter(
                        x=sub['passage'],
                        y=sub['expression'],
                        mode='lines+markers',
                        name=f"{p_sym} ({cond})",
                        line=dict(color=p_col, width=2.5, dash=line_style),
                        marker=dict(size=6)
                    ))
                    
        fig_multi.update_layout(
            title="Multi-Protein Trajectory Comparison (Solid = N, Dashed = A)",
            xaxis_title="Passage Number",
            yaxis_title="Mean Log₂ Abundance",
            template=PLOTLY_TEMPLATE,
            height=500
        )
        st.plotly_chart(fig_multi, use_container_width=True)
