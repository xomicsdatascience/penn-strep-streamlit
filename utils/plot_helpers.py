import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import CONDITION_COLORS, CONDITION_LABELS, PLOTLY_TEMPLATE

def create_volcano_plot(df, fdr_cutoff=0.01, coef_cutoff=0.0, highlight_gene=None, title="Volcano Plot"):
    """
    Generate an interactive Plotly Volcano Plot.
    df columns: protein, coef, pval_corrected, -log10_pval
    """
    plot_df = df.copy()
    
    # Categorize points based on thresholds
    conditions = [
        (plot_df['pval_corrected'] <= fdr_cutoff) & (plot_df['coef'] > coef_cutoff),
        (plot_df['pval_corrected'] <= fdr_cutoff) & (plot_df['coef'] < -coef_cutoff),
    ]
    choices = ['Up in Condition (p ≤ cutoff)', 'Down in Condition (p ≤ cutoff)']
    plot_df['Significance'] = np.select(conditions, choices, default='Not Significant')
    
    color_map = {
        'Up in Condition (p ≤ cutoff)': '#1976D2',       # Blue
        'Down in Condition (p ≤ cutoff)': '#D32F2F',     # Red
        'Not Significant': '#B0BEC5'                     # Light grey
    }
    
    fig = px.scatter(
        plot_df,
        x='coef',
        y='-log10_pval',
        color='Significance',
        color_discrete_map=color_map,
        hover_name='protein',
        hover_data={
            'coef': ':.3f',
            'pval_corrected': ':.2e',
            '-log10_pval': ':.2f',
            'Significance': False
        },
        labels={
            'coef': 'Effect Size (LME Coefficient)',
            '-log10_pval': '-log₁₀(Adjusted P-value)'
        },
        template=PLOTLY_TEMPLATE,
        height=550
    )
    
    # Threshold lines
    threshold_y = -np.log10(max(fdr_cutoff, 1e-300))
    fig.add_hline(
        y=threshold_y,
        line_dash="dash",
        line_color="#78909C",
        annotation_text=f"FDR = {fdr_cutoff}",
        annotation_position="bottom right"
    )
    
    if coef_cutoff > 0:
        fig.add_vline(x=coef_cutoff, line_dash="dash", line_color="#90A4AE")
        fig.add_vline(x=-coef_cutoff, line_dash="dash", line_color="#90A4AE")
        
    # Highlight specific gene if requested
    if highlight_gene and highlight_gene in plot_df['protein'].values:
        gene_row = plot_df[plot_df['protein'] == highlight_gene].iloc[0]
        fig.add_trace(go.Scatter(
            x=[gene_row['coef']],
            y=[gene_row['-log10_pval']],
            mode='markers+text',
            name=f'★ {highlight_gene}',
            text=[f'<b>{highlight_gene}</b>'],
            textposition='top center',
            marker=dict(size=14, color='#FFD600', symbol='star', line=dict(color='#000', width=1.5))
        ))
        
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family="sans-serif")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_pca_scatter(pca_df, color_by='condition', exp_var=(0.078, 0.060)):
    """Interactive PCA Scores Plot with customizable coloring."""
    pc1_pct = exp_var[0] * 100 if len(exp_var) > 0 else 0
    pc2_pct = exp_var[1] * 100 if len(exp_var) > 1 else 0
    
    color_map = CONDITION_COLORS if color_by == 'condition' else None
    
    fig = px.scatter(
        pca_df,
        x='PC1',
        y='PC2',
        color=color_by,
        color_discrete_map=color_map,
        hover_name='sample_id',
        hover_data={
            'plate': True,
            'passage': True,
            'condition': True,
            'detected_proteins': True,
            'PC1': ':.3f',
            'PC2': ':.3f'
        },
        labels={
            'PC1': f'PC1 ({pc1_pct:.1f}% Variance)',
            'PC2': f'PC2 ({pc2_pct:.1f}% Variance)'
        },
        template=PLOTLY_TEMPLATE,
        height=550
    )
    fig.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=0.8, color='white')))
    fig.update_layout(
        title=dict(text=f"Principal Component Analysis Scores Plot (Colored by {color_by.capitalize()})", font=dict(size=16)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_trajectory_plot(df_traj, protein_symbol, lme_stats=None):
    """
    Generate longitudinal expression trajectory across passages 1-9 for conditions A, N, AN, NA.
    """
    fig = go.Figure()
    
    for cond in ['A', 'N', 'AN', 'NA']:
        sub = df_traj[df_traj['condition'] == cond].sort_values('passage')
        if sub.empty:
            continue
            
        color = CONDITION_COLORS.get(cond, '#333')
        label = CONDITION_LABELS.get(cond, cond)
        
        # Calculate mean & standard deviation per passage
        stats = sub.groupby('passage')['expression'].agg(['mean', 'std']).reset_index()
        stats['std'] = stats['std'].fillna(0)
        
        # Add line for mean trajectory
        fig.add_trace(go.Scatter(
            x=stats['passage'],
            y=stats['mean'],
            mode='lines+markers',
            name=label,
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            error_y=dict(
                type='data',
                array=stats['std'],
                visible=True,
                color=color,
                thickness=1.5,
                width=4
            )
        ))
        
        # Add jittered individual replicate points
        fig.add_trace(go.Scatter(
            x=sub['passage'] + np.random.uniform(-0.08, 0.08, len(sub)),
            y=sub['expression'],
            mode='markers',
            name=f"{cond} Replicates",
            showlegend=False,
            marker=dict(size=5, color=color, opacity=0.45),
            hoverinfo='text',
            text=[f"Sample: {s}<br>Passage: {p}<br>Log2 Expr: {e:.2f}" for s, p, e in zip(sub['sample_id'], sub['passage'], sub['expression'])]
        ))
        
    title_text = f"Longitudinal Trajectory: {protein_symbol}"
    if lme_stats:
        title_text += f" | {lme_stats}"
        
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16)),
        xaxis=dict(
            title="Passage Number",
            tickmode='linear',
            tick0=1,
            dtick=1,
            gridcolor='#ECEFF1'
        ),
        yaxis=dict(
            title="Log₂ Protein Expression",
            gridcolor='#ECEFF1'
        ),
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=480,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_ranked_abundance_plot(df_expr, labeled_proteins=None):
    """Figure 2d: Ranked mean protein abundance curve with Plasma colormap and key labeled proteins."""
    means = df_expr.mean(axis=1).sort_values(ascending=False).reset_index()
    means.columns = ['protein', 'mean_expr']
    means['rank'] = means.index + 1
    
    fig = go.Figure()
    
    # Scatter points colored by rank with Plasma colormap exactly as in Cell 37:
    # scatter = plt.scatter(range(len(sorted_means)), sorted_means, c=colors, cmap=cm.plasma, s=20)
    fig.add_trace(go.Scatter(
        x=means['rank'],
        y=means['mean_expr'],
        mode='markers',
        marker=dict(
            size=4,
            color=means['rank'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(
                title=dict(text="Rank", side="right"),
                thickness=14,
                len=0.8
            )
        ),
        name='Protein Abundance Rank',
        hovertext=means['protein'],
        hovertemplate="<b>%{hovertext}</b><br>Rank: %{x}<br>Mean Expression (log₂): %{y:.2f}<extra></extra>"
    ))
    
    # Key proteins to label exactly as in Cell 37 and Figure 2d
    if labeled_proteins is None:
        labeled_proteins = ["ACTG1", "MAT2A", "CTSC", "CAVIN1", "ANXA3", "GCAT", "STEAP3", "HEXA", "NME4", "AKAP12", "BDP1"]
        
    labeled_df = means[means['protein'].isin(labeled_proteins)]
    
    # Add annotations with arrows for the labeled proteins
    for _, row in labeled_df.iterrows():
        p_name = row['protein']
        rank = row['rank']
        val = row['mean_expr']
        
        # Position annotations to avoid overlaps like adjust_text
        ay = -30 if p_name in ['ACTG1', 'MAT2A', 'ANXA3', 'NME4'] else 30
        ax = 25 if rank > 5000 else -25
        if p_name == 'ACTG1':
            ax = 30
            ay = -10
        elif p_name == 'BDP1':
            ax = -40
            ay = 20
            
        fig.add_annotation(
            x=rank,
            y=val,
            text=f"<b>{p_name}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.2,
            arrowcolor="#455A64",
            ax=ax,
            ay=ay,
            font=dict(size=12, color="#212121"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#B0BEC5",
            borderwidth=1,
            borderpad=2
        )
        
    fig.update_layout(
        title=dict(text="Figure 2d: Mean Protein Expression by Rank (Plasma Colormap)", font=dict(size=16)),
        xaxis=dict(
            title="Protein Rank",
            tickvals=[3000, 6000, 9000],
            range=[0, len(means) + 300],
            gridcolor='#ECEFF1'
        ),
        yaxis=dict(
            title="Mean Expression (log2)",
            tickvals=[15, 20, 25, 30],
            range=[10, 31],
            gridcolor='#ECEFF1'
        ),
        template=PLOTLY_TEMPLATE,
        height=540,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    return fig

def create_detection_histogram(metadata):
    """Figure 2b: Histogram of detected protein IDs across all 119 samples."""
    fig = px.histogram(
        metadata,
        x='detected_proteins',
        nbins=25,
        color_discrete_sequence=['#1976D2'],
        labels={'detected_proteins': 'Number of Detected Protein IDs'},
        template=PLOTLY_TEMPLATE,
        height=400
    )
    mean_val = metadata['detected_proteins'].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#388E3C",
        line_width=2,
        annotation_text=f"Mean: {mean_val:.0f}",
        annotation_position="top left"
    )
    fig.update_layout(
        title="Figure 2b: Detected Proteins per Sample (Mean ~9,374)",
        yaxis_title="Sample Count",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
