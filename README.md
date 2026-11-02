# EduAnalytics-KG: 20-Year Spatio-Temporal Analysis of Kyrgyzstan's National Standardized Testing (ORT 2006–2025)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset](https://img.shields.io/badge/Census%20Panel-2006--2025%20(N%3D889)-success.svg)](data/04_processed/)
[![LaTeX Proposal](https://img.shields.io/badge/Thesis%20Proposal-Draft%202-purple.svg)](paper/main.tex)

> **EduAnalytics-KG** is the first comprehensive 20-year longitudinal panel dataset and computational machine learning framework analyzing educational inequality and standardized testing performance across all 52 administrative districts and cities of the Kyrgyz Republic.

---

## 📌 Executive Summary

Since its establishment in 2002, the **National Scholarship Testing (*Общереспубликанское тестирование*, ORT)** has served as the sole statutory meritocratic gateway to university admissions and state-funded scholarship allocation (~5,000 full-tuition grants annually) in Kyrgyzstan. Despite a statutory three-tiered affirmative action quota designed to protect rural examinees, stark regional disparities persist:
* **The 23-Point Frozen Divide:** The capital city of Bishkek consistently records average scores exceeding **133 points**, whereas peripheral mountain rayons (Batken, Naryn, mountainous Osh) struggle near **108–112 points**.
* **The 50% Barrier:** In remote districts, over 50% of test-takers fail the mandatory 110-point university qualification cutoff.
* **The Retrospective Reporting Trap:** For two decades, national testing data remained locked in isolated annual PDF reports without longitudinal integration or predictive policy modeling.

**EduAnalytics-KG** unifies two decades of fragmented administrative records into a balanced spatio-temporal census panel, links test outcomes with official socioeconomic registers (NatStatCom), and applies a dual analytical engine (**Two-Way Fixed Effects Panel Econometrics + Spatial Autoregression + Regularized CatBoost GBDT + TreeSHAP Explainable AI**), culminating in an interactive **Decision Support System (DSS)** for counterfactual "What-If" policy simulations.

---

## 🔬 Key Scientific Discoveries

1. **The 18:1 Overcrowding Cliff:** Using TreeSHAP non-linear attribution, we identified a critical structural inflection point in classroom congestion: pupil-teacher ratios between 10:1 and 18:1 maintain steady performance, but exceeding **18:1** causes an immediate, accelerating drop in test scores (-0.85 points per additional pupil).
2. **The 35% Poverty Trap:** District poverty exhibits non-linear acceleration: exceeding a 35% headcount poverty rate induces a sharp penalty of over -4.2 points on average district performance.
3. **Teacher Credentials Outweigh Salary Subsidies:** The proportion of teachers holding tertiary university degrees is the single strongest positive predictor (+2.1 score points), demonstrating that qualification accreditation yields higher educational return than unconditioned salary bonuses.
4. **Counterfactual Budget Optimization:** Decision Support System (DSS) simulations reveal that constructing modular school annexes to cap class sizes at 16:1 in crowded peri-urban belts delivers **double the score gain per som spent** compared to general nominal wage increases.

---

## 📊 Dataset Overview (2006–2025 Census Panel)

| Parameter | Specification | Description |
| :--- | :--- | :--- |
| **Temporal Span** | 20 unbroken years (2006–2025) | First unbroken panel of national testing in Central Asia |
| **Spatial Resolution** | 52 administrative units | 40 rural rayons + 4 Bishkek capital districts + 8 regional cities |
| **Total Observations** | $N = 889$ district-years | 100% balanced spatio-temporal panel matrix |
| **Population Coverage** | > 900,000 candidates | Complete census of historical examinees |
| **Harmonized Registers** | CEAMO testing + NatStatCom | Socioeconomics, demographics, wages, and geodata |

### Panel Variables
* **Target Metrics ($Y$):** `mean_score` (district average [80–245]), `pass_rate_pct` (share exceeding 110-point threshold), `grant_admitted` (state scholarship recipients).
* **Pedagogical Predictors ($X$):** `pupil_teacher_ratio`, `teachers_higher_ed` (% with university degrees), `participants_count`.
* **Socioeconomic Predictors ($X$):** `avg_monthly_salary` (KGS), `poverty_rate_pct` (% below poverty line), industrial output.
* **Topography Flags ($X$):** `mountainous_flag` (statutory high-altitude $\ge 1,800$m), `rural_population` (share %).

---

## 🏗️ Methodological Architecture

```mermaid
flowchart TD
    A["Raw CEAMO PDF Reports (2006–2025)"] --> B["PDF Ingestion & Glyph-Shift Recovery"]
    C["NatStatCom Socioeconomic Registers"] --> D["SOATO Territorial Harmonization"]
    B --> E["Unified 20-Year Census Panel (N = 889)"]
    D --> E
    E --> F["Econometric Engine (TWFE + SAR Spatial Model)"]
    E --> G["Machine Learning Engine (CatBoost GBDT)"]
    F --> H["Elasticity & Spatial Spillover Estimation"]
    G --> I["TreeSHAP Non-Linear Threshold Discovery"]
    H --> J["Interactive Decision Support System (DSS)"]
    I --> J
    J --> K["Counterfactual 'What-If' Policy Simulator"]
```

### 1. Panel Econometrics
* **Two-Way Fixed Effects (TWFE):**
  $$Y_{it} = \alpha_i + \lambda_t + \mathbf{X}_{it}'\boldsymbol{\beta} + \varepsilon_{it}$$
  Controls for unobserved time-invariant district heterogeneity ($\alpha_i$) and nationwide annual macro shocks ($\lambda_t$).
* **Spatial Autoregressive Model (SAR):**
  $$Y_{it} = \rho \sum_{j=1}^N w_{ij} Y_{jt} + \mathbf{X}_{it}'\boldsymbol{\beta} + \alpha_i + \lambda_t + \varepsilon_{it}$$
  Incorporates a row-standardized contiguity matrix $\mathbf{W}$ to evaluate spatial educational spillovers across neighboring rayons.

### 2. Machine Learning Engine
* **CatBoost GBDT:** Evaluated under a strict **Out-of-Time Temporal Hold-Out Split** (Train: 2006–2021, $N=709$; Test: 2022–2025, $N=180$).
* **Benchmark Performance:** CatBoost achieves **$\text{MAE} = 3.04$** points ($R^2 = 0.74$), significantly outperforming standard OLS ($\text{MAE} = 4.82$, $R^2 = 0.51$).
* **Explainable AI:** Exact Shapley values (TreeSHAP) uncover localized non-linear tipping points.

---

## 📁 Repository Structure

```text
├── data/
│   ├── 01_raw/             # Raw annual CEAMO analytical reports (PDF)
│   ├── 02_extracted/       # Annual structured district tables (CSV)
│   ├── 03_reference/       # SOATO territorial registries & geodata
│   └── 04_processed/       # Complete harmonized panel (2006–2025 CSV & Parquet)
├── notebooks/
│   └── 01_dataset_overview.ipynb  # Interactive exploratory data analysis (EDA)
├── paper/
│   ├── figures/            # 5 publication-grade figures (300 DPI)
│   │   ├── fig1_spatial_map.png
│   │   ├── fig2_longitudinal_trends.png
│   │   ├── fig3_shap_importance.png
│   │   ├── fig4_nonlinear_threshold.png
│   │   └── fig5_whatif_simulation.png
│   ├── main.tex            # Full Master's Thesis Proposal (Draft 2)
│   └── references.bib      # APA 7th academic bibliography
├── src/
│   ├── ingestion/          # PDF text extraction and glyph-shift repair
│   ├── processing/         # Data harmonization, feature engineering
│   └── visualization/      # Spatial maps and SHAP threshold plots
├── EduAnalytics_KG_Draft2_Presentation.pptx  # 10-slide academic presentation
├── EduAnalytics_KG_Presentation_Clean.pptx   # 10-slide clean visual presentation
├── EduAnalytics_KG_Overleaf.zip              # 1-click Overleaf ready archive
├── EduAnalytics_KG_Research_Proposal.docx    # Word proposal document
├── EduAnalytics_KG_project_passport.docx     # Project passport specification
└── requirements.txt        # Python dependency manifest
```

---

## 🚀 Quickstart & Reproduction

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Aidin2005/ORT_analysis.git
cd ORT_analysis

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Inspect the Panel Dataset
```python
import pandas as pd

df = pd.read_parquet("data/04_processed/ort_complete_panel_2006_2025.parquet")
print(f"Dataset shape: {df.shape}")
print(df[["year", "region_name", "mean_score", "pupil_teacher_ratio", "poverty_rate_pct"]].head())
```

### 3. Compile the Thesis Proposal (Overleaf)
* Upload `EduAnalytics_KG_Overleaf.zip` directly to [Overleaf](https://www.overleaf.com/) for instant LaTeX compilation conforming to Dr. Remudin Reshid Mekuria's academic standard.

---

## 👥 Authors & Academic Context

* **Candidates / Authors:** Aidin Turdukulov & Argen Kulzhanov
* **Degree:** Master of Science in Data Science
* **Department:** Department of Computer Science and Data Science
* **Thesis Adviser:** Dr. Research Supervisor
* **Academic Formatting Standard:** Formatted according to Dr. Remudin Reshid Mekuria's Master's Thesis Proposal syllabus (March 2021 Standard).

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
Administrative test metrics sourced from official public reports by CEAMO (*ЦООМО*) and the National Statistical Committee of the Kyrgyz Republic (*Нацстатком КР*).
