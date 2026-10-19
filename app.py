import streamlit as st
import os
from config import (
    PAPER_TITLE,
    PAPER_AUTHORS,
    PAPER_JOURNAL,
    PAPER_CITATION,
    PAPER_DOI,
    CONDITION_COLORS
)

# Page configuration
st.set_page_config(
    page_title="HepG2 PenStrep Proteomics Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for clean, modern scientific UI
st.markdown("""
<style>
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E88E5;
    }
    
    /* Clean headers */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1A237E;
    }
    
    /* Sidebar branding */
    .sidebar-header {
        background: linear-gradient(135deg, #1A237E 0%, #283593 100%);
        padding: 18px 14px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar-header h2 {
        color: white !important;
        margin: 0;
        font-size: 1.25rem;
    }
    .sidebar-header p {
        color: #E8EAF6;
        margin: 5px 0 0 0;
        font-size: 0.85rem;
    }
    
    /* Quick badge */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>🔬 HepG2 PenStrep Explorer</h2>
        <p>Interactive Publication Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        [
            "🏠 Overview & Study Design (Fig 1)",
            "📊 Global Proteome & QC (Fig 2, S1-S2)",
            "🌋 LME Model & Volcano Plots (Fig 3, S10)",
            "📈 Longitudinal Trajectory Explorer",
            "🧬 Pathway Enrichment & GO (Fig 4, S13-S14)",
            "🔬 Literature Comparison (Fig 5, Tab 1)",
            "🧪 Lipid Metabolism Mechanism (Fig 6)",
            "🔍 Data Browser & Export"
        ],
        index=0
    )
    
    st.divider()
    
    st.markdown("### 📊 Dataset At A Glance")
    st.markdown("""
    - **Total Samples:** 119
    - **Total Proteins:** 10,255
    - **Avg Detected / Sample:** 9,374
    - **Duration:** 9 Passages (29 Days)
    - **Conditions:** A, N, AN, NA
    - **Platform:** Orbitrap Astral DIA-NN
    """)
    
    st.divider()
    
    st.markdown(f"**Citation:**")
    st.markdown(f"*{PAPER_AUTHORS}*")
    st.markdown(f"**[{PAPER_JOURNAL} (2026)]({PAPER_DOI})**")
    st.caption("Cedars-Sinai Medical Center, Los Angeles, CA")

# Route to selected view
if "Overview" in page:
    from views import overview
    overview.show()
elif "Global Proteome" in page:
    from views import global_qc
    global_qc.show()
elif "Volcano Plots" in page:
    from views import lme_volcano
    lme_volcano.show()
elif "Trajectory Explorer" in page:
    from views import trajectory
    trajectory.show()
elif "Pathway Enrichment" in page:
    from views import pathways
    pathways.show()
elif "Literature Comparison" in page:
    from views import literature
    literature.show()
elif "Lipid Metabolism" in page:
    from views import mechanism
    mechanism.show()
elif "Data Browser" in page:
    from views import data_export
    data_export.show()
