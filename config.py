"""
Configuration file for the PenStrep Streamlit Explorer.
Stores metadata, publication details, color palettes, and global constants.
"""

PAPER_TITLE = "Penicillin−Streptomycin Treatment Rewires Core Metabolic and Ribosomal Programs in HepG2 Cells"
PAPER_AUTHORS = "Cameron S. Movassaghi and Jesse G. Meyer*"
PAPER_JOURNAL = "Journal of Proteome Research"
PAPER_CITATION = "J. Proteome Res. 2026, 25, 2, 1082–1094"
PAPER_DOI = "https://doi.org/10.1021/acs.jproteome.5c00934"
PAPER_AFFILIATIONS = "Department of Computational Biomedicine & Advanced Clinical Biosystems Research Institute, Cedars-Sinai Medical Center, Los Angeles, CA"
CORRESPONDENCE = "Cameron.Movassaghi@cshs.org | Jesse.Meyer@cshs.org"

# Condition Color Palette matching the publication & cleaning notebook
CONDITION_COLORS = {
    "A": "#E57373",      # lightcoral: Continual PenStrep
    "N": "#64B5F6",      # cornflowerblue: Continual No Antibiotics
    "AN": "#FFB74D",     # sandybrown: Crossover from A -> N (passages 6-9)
    "NA": "#4DB6AC"      # cadetblue: Crossover from N -> A (passages 6-9)
}

CONDITION_LABELS = {
    "A": "A (Always Antibiotics, P1-9)",
    "N": "N (Always No Antibiotics, P1-9)",
    "AN": "AN (Crossover: Antibiotics P1-5 → No Antibiotics P6-9)",
    "NA": "NA (Crossover: No Antibiotics P1-5 → Antibiotics P6-9)"
}

CONDITION_DESCRIPTIONS = {
    "A": "HepG2 cells maintained continuously in 1% Penicillin-Streptomycin media.",
    "N": "HepG2 cells maintained continuously in antibiotic-free DMEM media.",
    "AN": "Treated with PenStrep for 5 passages, then switched to antibiotic-free media for passages 6–9.",
    "NA": "Grown without antibiotics for 5 passages, then switched to PenStrep-containing media for passages 6–9."
}

# Plate colors
PLATE_COLORS = {
    "P1": "#7E57C2",     # Purple
    "P2": "#26A69A"      # Teal
}

# Plotly theme configuration
PLOTLY_TEMPLATE = "plotly_white"
