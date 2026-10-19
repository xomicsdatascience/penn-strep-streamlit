# HepG2 PenStrep Proteomics Interactive Explorer

An interactive Streamlit web application accompanying the publication:

> **"Penicillin−Streptomycin Treatment Rewires Core Metabolic and Ribosomal Programs in HepG2 Cells"**  
> Cameron S. Movassaghi and Jesse G. Meyer*  
> *Journal of Proteome Research* 2026, 25 (2), 1082–1094.  
> [DOI: 10.1021/acs.jproteome.5c00934](https://doi.org/10.1021/acs.jproteome.5c00934)  
> *Department of Computational Biomedicine & Advanced Clinical Biosystems Research Institute, Cedars-Sinai Medical Center, Los Angeles, CA*

---

## 🚀 Quickstart

To launch the interactive Streamlit application:

```bash
# Ensure dependencies are installed
pip install streamlit pandas plotly openpyxl scikit-learn pyarrow PyMuPDF

# Run the Streamlit application
python -m streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 🔬 Study & Experimental Overview

Antibiotics like Penicillin-Streptomycin (PenStrep) are ubiquitously added to mammalian cell culture media. This study evaluated the proteome-wide consequences of antibiotic supplementation over a 29-day longitudinal study across 9 sequential passages in HepG2 cells using a crossover study design:

- **Condition A (Continual Antibiotics, P1–9):** Maintained in DMEM + 1% PenStrep.
- **Condition N (Continual No Antibiotics, P1–9):** Maintained in antibiotic-free DMEM.
- **Condition AN (Antibiotic Crossover, P6–9):** Cultured with PenStrep for 5 passages, then switched to antibiotic-free media for passages 6–9.
- **Condition NA (No Antibiotic Crossover, P6–9):** Cultured without antibiotics for 5 passages, then exposed to PenStrep for passages 6–9.
- **Proteomics Workflow:** 119 experimental samples + blanks and pooled quality controls (QCs), processed using single-pot solid-phase enhanced sample preparation (SP3) and analyzed by LC-MS/MS with a Thermo Scientific Orbitrap Astral operating in DIA mode (DIANN v1.8.1).

---

## 📊 Interactive Figures & Modules

| Module / View | Paper Figures | Key Interactive Capabilities |
| :--- | :--- | :--- |
| **🏠 Overview & Study Design** | **Figure 1** | Study abstract, highlights, timeline schematic of crossover design, sample counts by condition/passage/plate, and proteomics SP3 + Orbitrap Astral workflow details. |
| **📊 Global Proteome & QC** | **Figure 2**, **Figures S1–S2** | • Interactive boxplots of protein intensity across all 119 samples.<br>• Identification depth histogram (mean ~9,374 proteins/sample).<br>• Detection frequency distribution (7,606 core proteins detected in 100% of samples).<br>• Ranked abundance dynamic range curve with top labeled markers.<br>• 2D/3D PCA Scores plot (color by Condition, Passage, Plate) and PC1 loadings.<br>• Autosampler injection order QC stability and carryover assessment. |
| **🌋 LME Model & Volcano Plots** | **Figure 3**, **Figure S10** | • Linear mixed effects model (`FC_RI`) results.<br>• Three pairwise volcano plots (**NvA**, **NAvA**, **ANvA**) with customizable FDR cutoffs (0.001 to 0.10) and fold-change threshold sliders.<br>• Search box to locate and highlight any protein on the volcano plot.<br>• The **14 Core Consistently Altered Proteins** (GCAT, CPT1A, MAT2A, PDIA2, FAM3C, MTDH, CAVIN2, CRLF1, CTSC, HEXB, MTUS1, PLA2G15, SEMA3B, STEAP3) with localization, effect sizes, and mechanistic cards. |
| **📈 Longitudinal Trajectory Explorer** | **Figures 3c-d**, **Figures S7–S9** | • Interactive trajectory inspector for **any of the 10,255 proteins** across Passages 1 through 9.<br>• Visualizes adaptation dynamics upon antibiotic addition (NA) or withdrawal (AN).<br>• Multi-protein overlay comparison mode. |
| **🧬 Pathway Enrichment & GO** | **Figure 4**, **Figures S13–S14** | • Interactive bar plots of enriched terms across MSigDB Hallmark, GO Biological Process, Reactome, WikiPathways, and KEGG.<br>• Filter by direction (up in N vs up in A).<br>• Clickable pathways revealing key constituent proteins with direct links to trajectory analysis. |
| **🔬 Literature Comparison** | **Figure 5**, **Table 1** | • **Table 1:** Cross-study conserved proteins across 7 publications (*Ryu, Mathieson, Elliot, Relier, Kalghatgi, Han*).<br>• Comparison with Ryu et al. transcriptomics (7,503 overlapping genes, near-zero fold-change correlation $r = 0.02$). |
| **🧪 Lipid Metabolism Mechanism** | **Figure 6** | Integrative model of lipid transport (CD36, FABP1), de novo lipogenesis (ACACA, FASN, ACSL3), fatty acid beta-oxidation (CPT1A), oxidative stress defenses (GCAT, MAT2A, GPX2), and lysosomal lipophagy (HEXB, CTSC, PLA2G15). |
| **🔍 Data Browser & Export** | Supplementary Tables | Searchable table of the full proteomic matrix and LME model coefficients with one-click CSV export. |

---

## 📁 Repository Structure

```
penn-strep-streamlit/
├── app.py                     # Main Streamlit application entry point
├── config.py                  # Colors, plot styling, paper metadata
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # Robust cached data loaders & metadata parser
│   └── plot_helpers.py        # Reusable Plotly charts with unified theme
├── views/
│   ├── __init__.py
│   ├── overview.py            # Fig 1: Study Design & Proteomics Workflow
│   ├── global_qc.py           # Fig 2, S1-S2: Proteome Quant, Detection, PCA
│   ├── lme_volcano.py         # Fig 3, S10: Volcano Plots, Core 14 Proteins
│   ├── trajectory.py          # Longitudinal Trajectory Explorer (Fig 3c, S7-S9)
│   ├── pathways.py            # Fig 4, S13-S14: Enriched GO & Pathway Signatures
│   ├── literature.py          # Fig 5, Table 1: Cross-Study & Omics Validation
│   ├── mechanism.py           # Fig 6: Lipid Transport & Metabolic Rewiring
│   └── data_export.py         # Search, Filter, & Download Full Proteomic Matrix
├── data/
│   ├── cache/                 # Fast Parquet preprocessed data (instant loads)
│   ├── report.pg_matrix.tsv   # Raw DIANN quant data
│   └── pr5c00934_si_002.xlsx  # Linear model results
├── documents/
│   ├── pr5c00934.pdf          # Main paper
│   └── pr5c00934_si_001.pdf   # Supplementary information
└── assets/
    └── figures/               # Extracted high-res publication figures
```

---

## ⚙️ Data Cleaning & Conventions

Data cleaning follows the exact protocols published in the study's reference notebook ([hepg2_abc/1 Data import and cleaning.ipynb](https://github.com/xomicsdatascience/hepg2_abc/blob/main/1%20Data%20import%20and%20cleaning.ipynb)):
1. Multi-protein assignments (genes containing `;`) and NaN gene rows are removed.
2. Metadata columns (`Protein.Group`, `Protein.Names`, `First.Protein.Description`) dropped.
3. Raw file path prefixes/suffixes cleaned to extract sample tags (`P2_A5N4_5`, etc.).
4. Solvent blanks (`blank`), KF blanks (`BKF`), pooled QCs (`R`), and 7 DIANN-flagged outliers removed for experimental analysis.
5. Plate, passage ($A_n + N_n$), condition ($A$, $N$, $AN$, $NA$), and replicate parsed via regex.
6. 50% detection filter applied for statistical modeling ($9,518$ proteins).
