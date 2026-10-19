import os
import shutil
import json
import re
import pandas as pd
import numpy as np
import streamlit as st

CACHE_DIR = "data/cache"
RAW_TSV = "data/report.pg_matrix.tsv"
EXCEL_FILE = "data/pr5c00934_si_002.xlsx"
TEMP_EXCEL = "data/temp_si_002.xlsx"

@st.cache_data(show_spinner=False)
def load_metadata():
    """Load sample metadata for the 119 experimental samples."""
    path = os.path.join(CACHE_DIR, "metadata.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    # Fallback to direct extraction if cache not found
    ensure_data_cached()
    return pd.read_parquet(path)

@st.cache_data(show_spinner=False)
def load_expression_data(log2=True, filtered=True):
    """
    Load normalized protein expression matrix (proteins x samples).
    filtered: min 50% detection (9,518 proteins).
    log2: log2(1 + x) transformed.
    """
    if filtered:
        path = os.path.join(CACHE_DIR, "expression_log2.parquet" if log2 else "expression_filtered.parquet")
    else:
        path = os.path.join(CACHE_DIR, "expression_raw.parquet")
        
    if not os.path.exists(path):
        ensure_data_cached()
    df = pd.read_parquet(path)
    if log2 and not filtered:
        return np.log2(df.fillna(0) + 1)
    return df

@st.cache_data(show_spinner=False)
def load_pca_data():
    """Load PCA sample coordinates and loadings."""
    pca_samples_path = os.path.join(CACHE_DIR, "pca_samples.parquet")
    pca_loadings_path = os.path.join(CACHE_DIR, "pca_loadings.parquet")
    pca_info_path = os.path.join(CACHE_DIR, "pca_info.json")
    
    if os.path.exists(pca_samples_path) and os.path.exists(pca_loadings_path):
        samples_df = pd.read_parquet(pca_samples_path)
        loadings_df = pd.read_parquet(pca_loadings_path)
        with open(pca_info_path, 'r') as f:
            info = json.load(f)
        return samples_df, loadings_df, info['explained_variance_ratio']
    
    ensure_data_cached()
    samples_df = pd.read_parquet(pca_samples_path)
    loadings_df = pd.read_parquet(pca_loadings_path)
    with open(pca_info_path, 'r') as f:
        info = json.load(f)
    return samples_df, loadings_df, info['explained_variance_ratio']

@st.cache_data(show_spinner=False)
def load_lme_data(comparison=None):
    """
    Load linear mixed effects model results from Excel.
    comparison: 'NvA', 'NAvA', 'ANvA', or None for all.
    """
    path = os.path.join(CACHE_DIR, "lme_all.parquet")
    if not os.path.exists(path):
        ensure_data_cached()
    df = pd.read_parquet(path)
    if comparison:
        return df[df['comparison'] == comparison].copy()
    return df

@st.cache_data(show_spinner=False)
def load_core14_proteins():
    """Load the 14 core proteins consistently differentially abundant across comparisons."""
    path = os.path.join(CACHE_DIR, "core14_proteins.parquet")
    if not os.path.exists(path):
        ensure_data_cached()
    return pd.read_parquet(path)

@st.cache_data(show_spinner=False)
def load_table1_literature():
    """Load Table 1 literature comparison across published studies."""
    path = os.path.join(CACHE_DIR, "table1_literature.parquet")
    if not os.path.exists(path):
        ensure_data_cached()
    return pd.read_parquet(path)

@st.cache_data(show_spinner=False)
def load_pathways_data():
    """Load Figure 4 pathway enrichment terms and stats."""
    path = os.path.join(CACHE_DIR, "pathways_figure4.parquet")
    if not os.path.exists(path):
        ensure_data_cached()
    return pd.read_parquet(path)

@st.cache_data(show_spinner=False)
def load_blanks_and_qcs():
    """Load solvent blanks, KF blanks, and pooled QCs expression data."""
    path = os.path.join(CACHE_DIR, "blanks_qcs.parquet")
    if not os.path.exists(path):
        ensure_data_cached()
    return pd.read_parquet(path)

def get_protein_trajectory(protein_symbol, df_expr=None, metadata=None):
    """
    Extract longitudinal trajectory for a given protein across all 119 samples.
    Returns merged dataframe sorted by passage and condition.
    """
    if df_expr is None:
        df_expr = load_expression_data(log2=True, filtered=False)
    if metadata is None:
        metadata = load_metadata()
        
    if protein_symbol not in df_expr.index:
        return None
        
    series = df_expr.loc[protein_symbol]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[0]
    df_traj = metadata.copy()
    df_traj['expression'] = series.values
    df_traj['protein'] = protein_symbol
    return df_traj

def ensure_data_cached():
    """Ensures cached parquet files exist; generates them if missing."""
    if os.path.exists(os.path.join(CACHE_DIR, "metadata.parquet")):
        return
    # If not present, run preprocessing script
    import subprocess
    subprocess.run(["python", "scratch/prepare_data.py"], check=True)
    subprocess.run(["python", "scratch/save_tables.py"], check=True)
