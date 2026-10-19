import streamlit as st
import pandas as pd
import os
from config import PAPER_TITLE, PAPER_AUTHORS, PAPER_JOURNAL, PAPER_CITATION, PAPER_DOI, CONDITION_DESCRIPTIONS, CONDITION_COLORS
from utils.data_loader import load_metadata

def show():
    st.markdown(f"## 🔬 Study Overview & Experimental Design")
    st.markdown(f"**Publication:** *{PAPER_TITLE}*")
    st.markdown(f"*{PAPER_AUTHORS}* | [{PAPER_CITATION}]({PAPER_DOI})")
    
    st.divider()
    
    # Key Highlights Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Samples Analyzed", value="119", help="Across 9 passages and 4 conditions")
    with col2:
        st.metric(label="Total Proteins Detected", value="10,255", help="Identified via Astral DIA-NN")
    with col3:
        st.metric(label="Average Proteins / Sample", value="9,374", help="High depth and proteome coverage")
    with col4:
        st.metric(label="Differentially Abundant", value="139", help="Unique proteins with FDR ≤ 0.01 (383 at FDR ≤ 0.1)")

    st.markdown("""
    ### 📌 Abstract & Research Rationale
    Antibiotics (such as **Penicillin-Streptomycin / PenStrep**) are routinely added to mammalian cell culture media to prevent bacterial contamination. 
    However, the long-term off-target consequences on the mammalian proteome have remained largely uncharacterized.
    
    In this study, HepG2 cells were monitored longitudinally across **9 sequential passages** using a **crossover study design**:
    - **A (Always Antibiotics):** Cells grown continually in media containing 1% PenStrep.
    - **N (Always No Antibiotics):** Cells grown in antibiotic-free media.
    - **AN (Antibiotic Crossover):** Cells cultured in PenStrep for 5 passages, then switched to antibiotic-free media for passages 6–9.
    - **NA (Non-Antibiotic Crossover):** Cells cultured without antibiotics for 5 passages, then exposed to PenStrep for passages 6–9.
    
    Using high-throughput **SP3 sample preparation** and ultra-deep **Orbitrap Astral DIA-NN** mass spectrometry, this study reveals that 
    antibiotic exposure selectively rewires core metabolic, mitochondrial, and ribosomal machinery at the protein level.
    """)
    
    st.markdown("### 📊 Figure 1: Experimental Design & Workflow")
    fig1_path = "assets/figures/fig1_experimental_overview.png"
    if os.path.exists(fig1_path):
        st.image(fig1_path, caption="Figure 1: (a) Longitudinal crossover culture design across 9 passages. (b) Proteomics workflow using SP3 and Orbitrap Astral LC-MS/MS.", use_container_width=True)
        
    st.markdown("### 🧬 Experimental Condition Breakdown")
    meta = load_metadata()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### Sample Counts by Condition")
        cond_counts = meta['condition'].value_counts().reset_index()
        cond_counts.columns = ['Condition', 'Sample Count']
        cond_counts['Description'] = cond_counts['Condition'].map(CONDITION_DESCRIPTIONS)
        st.dataframe(cond_counts, hide_index=True, use_container_width=True)
        
    with c2:
        st.markdown("#### Passages & Replicates Breakdown")
        cross_tab = pd.crosstab(meta['passage'], meta['condition'])
        cross_tab.index.name = "Passage"
        st.dataframe(cross_tab, use_container_width=True)
        
    with st.expander("ℹ️ Details on Sample Preparation & MS Acquisition"):
        st.markdown("""
        - **Cell Line:** HepG2 (human hepatocellular carcinoma), seeded at ~0.2 × 10⁶ cells/well in 6-well plates and harvested at >80% confluency (~1.2 × 10⁶ cells).
        - **Sample Preparation:** Single-pot, solid-phase enhanced sample preparation (SP3) using carboxylate-modified magnetic beads.
        - **Digestion:** Trypsin/Lys-C enzymatic digestion.
        - **Chromatography & MS:** Vanquish Neo UHPLC coupled to a Thermo Scientific Orbitrap Astral mass spectrometer operating in data-independent acquisition (DIA) mode.
        - **Spectral Library & Processing:** DIANN v1.8.1 against the UniProt human proteome database.
        """)
