"""
Generate an executive mini-presentation for the EduAnalytics-KG Research Project.
Creates widescreen (16:9) professional slides with clean typography and structured cards.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path: Path):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color Palette
    C_DARK_BG = RGBColor(15, 23, 42)       # Slate 900
    C_LIGHT_BG = RGBColor(248, 250, 252)   # Slate 50
    C_WHITE = RGBColor(255, 255, 255)
    C_NAVY = RGBColor(30, 58, 138)         # Blue 900
    C_BLUE = RGBColor(2, 132, 199)         # Sky 600
    C_TEAL = RGBColor(13, 148, 136)        # Teal 600
    C_TEXT_DARK = RGBColor(30, 41, 59)     # Slate 800
    C_TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    C_CARD_BG = RGBColor(255, 255, 255)
    C_CARD_BORDER = RGBColor(226, 232, 240)# Slate 200
    C_ACCENT_BG = RGBColor(241, 245, 249)  # Slate 100

    def set_slide_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, category: str, title: str, subtitle: str = ""):
        # Category pill/tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE
        
        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_DARK

        if subtitle:
            p_sub = tf_title.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = C_TEXT_MUTED
            p_sub.space_before = Pt(4)

    # ----------------------------------------------------
    # SLIDE 1: Title Slide (Dark Theme)
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_DARK_BG)

    # Decorative accent line
    accent = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(1.5), Inches(0.08))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_BLUE
    accent.line.fill.background()

    # Main Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "EduAnalytics-KG"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Spatial-Temporal Analysis of National Standardized Testing (ORT) and Decision Support Modeling for Educational Equity in Kyrgyzstan"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(16)

    # Meta card / pills
    meta_box = s1.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(11.3), Inches(1.5))
    tf_meta = meta_box.text_frame
    tf_meta.word_wrap = True
    pm1 = tf_meta.paragraphs[0]
    pm1.text = "20-Year Longitudinal Study (2006–2025)  •  Machine Learning & Explainable AI (SHAP)  •  Interactive DSS Prototype"
    pm1.font.size = Pt(14)
    pm1.font.bold = True
    pm1.font.color.rgb = C_TEAL

    pm2 = tf_meta.add_paragraph()
    pm2.text = "Evidence-Based Policy Modeling  |  Kyrgyz Republic Education System"
    pm2.font.size = Pt(13)
    pm2.font.color.rgb = RGBColor(148, 163, 184)
    pm2.space_before = Pt(8)

    # ----------------------------------------------------
    # SLIDE 2: Context & The Core Problem
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, C_LIGHT_BG)
    add_header(s2, "Research Motivation", "The Challenge of Regional Educational Inequality", 
               "Over 20 years of standardized testing reveals structural academic disparities across Kyrgyzstan.")

    cards_s2 = [
        ("20+ Years of Standardized Testing", 
         "Since 2002, the National Testing (ORT) has served as the sole objective gateway for state university scholarships, testing over 500,000 high school graduates.",
         C_NAVY),
        ("Persistent Regional Disparities", 
         "Significant and persistent performance gaps exist between Bishkek, regional capitals, and remote rural/mountainous schools across all seven oblasts.",
         C_BLUE),
        ("The Analytical Gap", 
         "Historical data remained fragmented in annual PDF reports with no unified machine-readable panel or predictive tools to evaluate policy interventions.",
         C_TEAL)
    ]

    for i, (ctitle, cdesc, ccolor) in enumerate(cards_s2):
        left = Inches(0.8 + i * 3.95)
        top = Inches(2.2)
        width = Inches(3.75)
        height = Inches(4.5)

        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        # Header bar
        hbar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.1))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = ccolor
        hbar.line.fill.background()

        tb = s2.shapes.add_textbox(left + Inches(0.3), top + Inches(0.4), width - Inches(0.6), height - Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK

        p_desc = tf.add_paragraph()
        p_desc.text = cdesc
        p_desc.font.size = Pt(14)
        p_desc.font.color.rgb = C_TEXT_MUTED
        p_desc.space_before = Pt(14)

    # ----------------------------------------------------
    # SLIDE 3: Research Questions (RQs)
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, C_LIGHT_BG)
    add_header(s3, "Theoretical Foundation", "Core Research Questions (RQs)", 
               "Guiding inquiries formulated in the project passport to drive empirical discovery.")

    rqs = [
        ("RQ1", "Spatial-Temporal Inequality", 
         "How have regional and rural-urban academic performance gaps evolved across Kyrgyzstan's 48 administrative territories between 2006 and 2025? Are regions converging or diverging?"),
        ("RQ2", "Predictive Socio-Demographic Drivers", 
         "Which subnational socioeconomic, infrastructural, and pedagogical features (e.g., pupil-teacher ratios, educator credentials, household income) most strongly associate with test score variance?"),
        ("RQ3", "Geographic & Temporal Generalization", 
         "Can machine learning models trained on specific historical epochs or regions accurately generalize out-of-sample to other geographic zones and future years without performance degradation?")
    ]

    for i, (badge, title, desc) in enumerate(rqs):
        top = Inches(2.0 + i * 1.65)
        left = Inches(0.8)
        width = Inches(11.73)
        height = Inches(1.4)

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER

        # Badge
        b_box = s3.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), Inches(1.2), Inches(0.5))
        tf_b = b_box.text_frame
        pb = tf_b.paragraphs[0]
        pb.text = badge
        pb.font.size = Pt(18)
        pb.font.bold = True
        pb.font.color.rgb = C_BLUE

        # Content
        c_box = s3.shapes.add_textbox(left + Inches(1.5), top + Inches(0.15), width - Inches(1.8), height - Inches(0.3))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        pt = tf_c.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = C_TEXT_DARK

        pd = tf_c.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(13)
        pd.font.color.rgb = C_TEXT_MUTED
        pd.space_before = Pt(4)

    # ----------------------------------------------------
    # SLIDE 4: The Dataset: Newly Curated Panel
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, C_LIGHT_BG)
    add_header(s4, "Data Engineering", "The Assembled 20-Year Longitudinal Dataset", 
               "Successfully mined, parsed, standardized, and harmonized into an analytical panel.")

    # 4 Stat callout boxes
    stats = [
        ("760", "District-Year Rows", "Balanced panel observations"),
        ("48", "Territorial Units", "All districts & major cities"),
        ("17 Years", "Longitudinal Span", "2006–2025 continuous series"),
        ("~500k", "Students Represented", "Standardized test records")
    ]

    for i, (num, label, sub) in enumerate(stats):
        left = Inches(0.8 + i * 2.95)
        top = Inches(2.0)
        width = Inches(2.8)
        height = Inches(1.6)

        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_CARD_BORDER

        tb = s4.shapes.add_textbox(left, top + Inches(0.15), width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = num
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(30)
        p1.font.bold = True
        p1.font.color.rgb = C_BLUE

        p2 = tf.add_paragraph()
        p2.text = label
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_DARK

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.alignment = PP_ALIGN.CENTER
        p3.font.size = Pt(11)
        p3.font.color.rgb = C_TEXT_MUTED

    # Bottom detailed split
    b_left = Inches(0.8)
    b_top = Inches(4.0)
    b_w = Inches(11.73)
    b_h = Inches(2.8)
    bbox = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, b_left, b_top, b_w, b_h)
    bbox.fill.solid()
    bbox.fill.fore_color.rgb = C_WHITE
    bbox.line.color.rgb = C_CARD_BORDER

    tb_b = s4.shapes.add_textbox(b_left + Inches(0.4), b_top + Inches(0.3), b_w - Inches(0.8), b_h - Inches(0.6))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    pb1 = tf_b.paragraphs[0]
    pb1.text = "Key Dataset Dimensions & Variables"
    pb1.font.size = Pt(17)
    pb1.font.bold = True
    pb1.font.color.rgb = C_TEXT_DARK

    bullets = [
        "Academic Metrics: Mean composite score, % scoring above national passing threshold (110 pts), state scholarship recipients.",
        "Spatial Identifiers: Official SOATO national statistical codes, canonical administrative IDs, and linked ADM1/ADM2 GeoJSON vectors.",
        "Socioeconomic Covariates: Subnational student-teacher ratios, teacher education profiles, poverty headcounts, and rurality indexes.",
        "Production Formats: Dual delivery in open CSV and high-performance columnar Apache Parquet."
    ]
    for b in bullets:
        p = tf_b.add_paragraph()
        p.text = "•  " + b
        p.font.size = Pt(13)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_before = Pt(6)

    # ----------------------------------------------------
    # SLIDE 5: Methodology & Machine Learning
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, C_LIGHT_BG)
    add_header(s5, "Methodology & Architecture", "Machine Learning & Explainable AI Pipeline", 
               "From automated ETL extraction to gradient boosting and spatial generalization.")

    steps = [
        ("1. Spatio-Temporal EDA", "Descriptive trends, regional convergence analysis, and spatial autocorrelation (Moran's I) across districts."),
        ("2. Supervised Learning", "Gradient-boosted decision trees (CatBoost, LightGBM) modeling complex non-linear relationships with strict regularization."),
        ("3. Explainable AI (SHAP)", "Global & local feature importance attribution to isolate resource contributions without confusing correlation for causation."),
        ("4. Spatial & Temporal Validation", "Rigorous out-of-time (pre-2020 vs post-2020) and out-of-region (North vs South) holdouts to detect overfitting."),
        ("5. Positive Deviance Analysis", "Statistical residual analysis to isolate districts outperforming expectation despite socioeconomic constraints.")
    ]

    for i, (stitle, sdesc) in enumerate(steps):
        top = Inches(2.0 + i * 1.0)
        left = Inches(0.8)
        width = Inches(11.73)
        height = Inches(0.85)

        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER

        tb = s5.shapes.add_textbox(left + Inches(0.3), top + Inches(0.12), width - Inches(0.6), height)
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = stitle + ": "
        pt.font.size = Pt(14)
        pt.font.bold = True
        pt.font.color.rgb = C_BLUE

        run = pt.add_run()
        run.text = sdesc
        run.font.bold = False
        run.font.color.rgb = C_TEXT_DARK

    # ----------------------------------------------------
    # SLIDE 6: Applied Deliverable: Decision Support System
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, C_LIGHT_BG)
    add_header(s6, "Applied Impact", "Decision Support System (DSS) & What-If Simulator", 
               "A web-based analytical prototype translating empirical models into actionable policy tools.")

    dss_modules = [
        ("Interactive Geospatial Dashboard", 
         "Dynamic choropleth map of Kyrgyzstan visualizing district-level performance across all 20 years with multi-metric filtering.",
         C_NAVY),
        ("What-If Scenario Engine", 
         "Interactive policy simulation: test interventions (e.g., reducing teacher burden by 15%, targeted salary supplements) and preview model-projected outcomes.",
         C_BLUE),
        ("SHAP Intervention Transparency", 
         "Live waterfall plots showing exactly which policy levers contributed to projected score shifts, with clear causal caveat disclaimers.",
         C_TEAL)
    ]

    for i, (dtitle, ddesc, dcolor) in enumerate(dss_modules):
        left = Inches(0.8 + i * 3.95)
        top = Inches(2.2)
        width = Inches(3.75)
        height = Inches(4.5)

        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        # Header bar
        hbar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.1))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = dcolor
        hbar.line.fill.background()

        tb = s6.shapes.add_textbox(left + Inches(0.3), top + Inches(0.4), width - Inches(0.6), height - Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = dtitle
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK

        p_desc = tf.add_paragraph()
        p_desc.text = ddesc
        p_desc.font.size = Pt(14)
        p_desc.font.color.rgb = C_TEXT_MUTED
        p_desc.space_before = Pt(14)

    # ----------------------------------------------------
    # SLIDE 7: Scientific Novelty & Policy Value
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, C_LIGHT_BG)
    add_header(s7, "Contribution", "Scientific Novelty & Practical Relevance", 
               "Bridging educational sociology, data engineering, and public policy.")

    # Left card: Scientific Novelty
    w_half = Inches(5.7)
    c1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), w_half, Inches(4.5))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_WHITE
    c1.line.color.rgb = C_CARD_BORDER

    tb1 = s7.shapes.add_textbox(Inches(1.1), Inches(2.5), w_half - Inches(0.6), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Academic & Methodological Novelty"
    p1.font.size = Pt(19)
    p1.font.bold = True
    p1.font.color.rgb = C_NAVY

    nov_pts = [
        "First 20-year longitudinal spatio-temporal panel of national standardized testing in Central Asia.",
        "Methodological separation between predictive association and causal inference using Explainable AI (SHAP).",
        "Systematic evaluation of geographic out-of-domain transferability in educational machine learning models."
    ]
    for pt in nov_pts:
        p = tf1.add_paragraph()
        p.text = "•  " + pt
        p.font.size = Pt(13)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_before = Pt(12)

    # Right card: Practical Significance
    c2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.2), w_half, Inches(4.5))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_WHITE
    c2.line.color.rgb = C_CARD_BORDER

    tb2 = s7.shapes.add_textbox(Inches(7.1), Inches(2.5), w_half - Inches(0.6), Inches(4.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "Practical & Policy Significance"
    p2.font.size = Pt(19)
    p2.font.bold = True
    p2.font.color.rgb = C_TEAL

    pol_pts = [
        "Provides the Ministry of Education with an evidence-based roadmap for targeting resource allocation.",
        "Identifies positive deviant districts whose local teaching practices can be replicated nationwide.",
        "Interactive scenario simulator allows decision-makers to evaluate budget trade-offs prior to commitment."
    ]
    for pt in pol_pts:
        p = tf2.add_paragraph()
        p.text = "•  " + pt
        p.font.size = Pt(13)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_before = Pt(12)

    # ----------------------------------------------------
    # SLIDE 8: Status & Next Milestones
    # ----------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, C_LIGHT_BG)
    add_header(s8, "Roadmap", "Current Milestones & Next Steps", 
               "Solid foundation completed; ready for advanced modeling and application development.")

    steps_m = [
        ("Phase 1: Ingestion & Panel Assembly", "COMPLETED", 
         "Extracted 20 years of testing reports, harmonized 48 districts with SOATO codes, and verified panel datasets (CSV/Parquet).", C_TEAL),
        ("Phase 2: Socioeconomic Enrichment", "IN PROGRESS", 
         "Merging National Statistical Committee indicators (pupil-teacher ratios, regional salaries, poverty headcounts) into the ML matrix.", C_BLUE),
        ("Phase 3: Machine Learning & SHAP", "UPCOMING", 
         "Training baseline & CatBoost regressors, conducting geographic generalization experiments, and generating SHAP feature contributions.", C_NAVY),
        ("Phase 4: Decision Support System (DSS)", "UPCOMING", 
         "Deploying interactive Streamlit dashboard featuring choropleth GIS mapping and the What-If policy simulation engine.", C_DARK_BG)
    ]

    for i, (mtitle, mbadge, mdesc, mcolor) in enumerate(steps_m):
        top = Inches(2.0 + i * 1.25)
        left = Inches(0.8)
        width = Inches(11.73)
        height = Inches(1.05)

        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_CARD_BORDER

        # Status badge
        badge_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.3), top + Inches(0.2), Inches(1.8), Inches(0.35))
        badge_box.fill.solid()
        badge_box.fill.fore_color.rgb = mcolor
        badge_box.line.fill.background()

        tf_bg = badge_box.text_frame
        p_bg = tf_bg.paragraphs[0]
        p_bg.text = mbadge
        p_bg.alignment = PP_ALIGN.CENTER
        p_bg.font.size = Pt(11)
        p_bg.font.bold = True
        p_bg.font.color.rgb = C_WHITE

        # Content
        c_box = s8.shapes.add_textbox(left + Inches(2.3), top + Inches(0.12), width - Inches(2.6), height - Inches(0.2))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        pt = tf_c.paragraphs[0]
        pt.text = mtitle
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = C_TEXT_DARK

        pd = tf_c.add_paragraph()
        pd.text = mdesc
        pd.font.size = Pt(12)
        pd.font.color.rgb = C_TEXT_MUTED
        pd.space_before = Pt(3)

    # Save presentation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"✓ Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    out_file = Path("EduAnalytics_KG_Presentation.pptx")
    create_deck(out_file)
