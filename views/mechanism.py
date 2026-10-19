import streamlit as st
import os

def show():
    st.markdown("## 🧪 Proposed Biological Mechanism: Lipid & Metabolic Rewiring")
    st.markdown("""
    Explore **Figure 6**: integrative model of the dysregulated protein pathways involved in 
    lipid transport, mitochondrial fatty acid oxidation, oxidative stress, and autophagy in HepG2 cells 
    following penicillin-streptomycin exposure.
    """)
    
    tab1, tab2 = st.tabs(["🗺️ Metabolic Wiring Diagram & Pathways", "🖼️ Publication Figure 6"])
    
    with tab1:
        st.markdown("### Integrative Model of HepG2 Lipid & Metabolic Remodeling")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("""
            #### 🔴 Pathways Upregulated by Antibiotics (A)
            - **Mitochondrial Fatty Acid Beta-Oxidation:** 
              - **CPT1A** (rate-limiting carnitine palmitoyltransferase) is significantly elevated, driving mitochondrial fatty acid uptake and oxidation.
              - Accelerated beta-oxidation increases electron flux, contributing to **reactive oxygen species (ROS)** accumulation and mitochondrial stress.
            - **Glutathione Defense Adaptation:**
              - **GCAT** (glycine C-acetyltransferase) is strongly upregulated (coef = -1.50, p = 1.5e-24) to generate glycine, feeding into glutathione synthesis to mitigate ROS.
            - **Lysosomal Lipid Catabolism & Lipophagy:**
              - **CTSC** (cathepsin C), **HEXB** (hexosaminidase B), and **PLA2G15** (phospholipase A2) are increased, facilitating degradation of stored lipid droplets.
            - **Endosomal / Stress Markers:**
              - **STEAP3** (ferrireductase / p53 signaling) and **CAVIN2** are altered.
            """)
            
        with c2:
            st.markdown("""
            #### 🔵 Pathways Upregulated in Non-Antibiotics (N)
            - **De Novo Lipogenesis (ChREBP Pathway):**
              - **ACACA** (acetyl-CoA carboxylase) and **FASN** (fatty acid synthase) generate malonyl-CoA and palmitate.
              - Malonyl-CoA is a potent physiological inhibitor of CPT1A, restricting beta-oxidation in healthy basal conditions.
              - **ACSL3** promotes fatty acyl-CoA incorporation into neutral lipids on lipid droplets.
            - **One-Carbon & Methionine Metabolism:**
              - **MAT2A** is elevated in N, producing S-adenosylmethionine (SAM) for trans-sulfuration to cysteine and transcriptional methylation.
            - **VLDL Assembly & Exocytosis:**
              - **PLIN2** (perilipin) and **MTTP** package triglycerides into **APOB** to form VLDL for exocytosis.
              - Vesicle trafficking machinery (**RAB2B, RAB17, RAB22A, SEC11C, SEC31A, SEC61B**) is increased in N to support secretory transport.
            """)
            
        st.divider()
        
        st.markdown("### 🔍 Key Molecular Nodes in the Pathway")
        nodes = [
            {
                "Node": "CPT1A",
                "Name": "Carnitine Palmitoyltransferase 1A",
                "Role": "Mitochondrial Fatty Acid Gatekeeper",
                "Shift": "Upregulated in PenStrep (A)",
                "Color": "🔴",
                "Impact": "Accelerates long-chain fatty acid entry into mitochondria, promoting beta-oxidation and superoxide / ROS generation."
            },
            {
                "Node": "GCAT",
                "Name": "Glycine C-acetyltransferase",
                "Role": "Threonine Degradation & Glycine Supply",
                "Shift": "Upregulated in PenStrep (A)",
                "Color": "🔴",
                "Impact": "Generates glycine in mitochondria to supply tripeptide glutathione synthesis under oxidative stress."
            },
            {
                "Node": "MAT2A",
                "Name": "Methionine Adenosyltransferase 2A",
                "Role": "Methionine Cycle & SAM Synthesis",
                "Shift": "Downregulated in PenStrep (Higher in N)",
                "Color": "🔵",
                "Impact": "Catalyzes SAM formation; reduced in antibiotics, potentially compromising cellular methylation and cysteine flux."
            },
            {
                "Node": "ACSL3",
                "Name": "Acyl-CoA Synthetase Long Chain 3",
                "Role": "Lipid Droplet Formation",
                "Shift": "Downregulated in PenStrep (Higher in N)",
                "Color": "🔵",
                "Impact": "Channels fatty acids into triglyceride storage in lipid droplets rather than mitochondrial oxidation."
            },
            {
                "Node": "CTSC & HEXB",
                "Name": "Cathepsin C & Beta-Hexosaminidase",
                "Role": "Lysosomal Autophagy & Lipophagy",
                "Shift": "Upregulated in PenStrep (A)",
                "Color": "🔴",
                "Impact": "Mediates lysosomal breakdown of lipid droplet components under stress."
            }
        ]
        
        for n in nodes:
            with st.expander(f"{n['Color']} **{n['Node']}** — {n['Name']} ({n['Role']})"):
                st.markdown(f"**Expression Shift:** {n['Shift']}")
                st.markdown(f"**Mechanism & Impact:** {n['Impact']}")

    with tab2:
        st.markdown("### Publication Figure 6: Dysregulated Lipid Transport & Metabolism")
        fig6_path = "assets/figures/fig6_lipid_metabolism_pathway.png"
        if os.path.exists(fig6_path):
            st.image(fig6_path, caption="Figure 6: Dysregulated protein pathways involved in lipid transport and metabolism in HepG2 cells with (red) or without (blue) antibiotics.", use_container_width=True)
