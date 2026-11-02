"""
Generate comprehensive research concept document (DOCX) for academic supervisor / professor.
Covers:
1. Core project idea
2. Global analogues (SAT, ENEM, Saber 11, PISA) and problems they solve
3. Specificity and scientific novelty of our study (Kyrgyzstan context)
4. Key findings and demonstrations to present in the paper
5. Current progress and assembled data assets
"""

import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal padding for table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document(output_path: Path):
    doc = Document()

    # Set standard margins (2 cm)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Styles
    COLOR_PRIMARY = RGBColor(30, 58, 138)    # Deep Navy
    COLOR_SECONDARY = RGBColor(15, 23, 42)  # Dark Slate
    COLOR_MUTED = RGBColor(71, 85, 105)     # Slate 600

    # Document Header / Title
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_pre = p_pre.add_run("Научно-исследовательский проект (Research Proposal)")
    r_pre.font.name = "Calibri"
    r_pre.font.size = Pt(10)
    r_pre.font.color.rgb = COLOR_MUTED

    title_p = doc.add_paragraph()
    title_r = title_p.add_run("EduAnalytics-KG: Пространственно-временной анализ результатов ОРТ и предиктивное моделирование в сфере образования Кыргызской Республики (2006–2025 гг.)")
    title_r.font.name = "Calibri"
    title_r.font.size = Pt(20)
    title_r.font.bold = True
    title_r.font.color.rgb = COLOR_PRIMARY
    title_p.paragraph_format.space_after = Pt(4)

    sub_p = doc.add_paragraph()
    sub_r = sub_p.add_run("Научно-методическое обоснование проекта для научного руководителя")
    sub_r.font.name = "Calibri"
    sub_r.font.size = Pt(13)
    sub_r.font.italic = True
    sub_r.font.color.rgb = COLOR_MUTED
    sub_p.paragraph_format.space_after = Pt(18)

    # Helper function for headings
    def add_h1(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        return h

    def add_p(text, bold_prefix="", italic_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = "Calibri"
            r_b.font.size = Pt(11)
            r_b.font.bold = True
            r_b.font.color.rgb = COLOR_SECONDARY
        if italic_prefix:
            r_i = p.add_run(italic_prefix)
            r_i.font.name = "Calibri"
            r_i.font.size = Pt(11)
            r_i.font.italic = True
            r_i.font.color.rgb = COLOR_MUTED
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_SECONDARY
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        rb = p.add_run(bold_prefix + " ")
        rb.font.name = "Calibri"
        rb.font.size = Pt(11)
        rb.font.bold = True
        rb.font.color.rgb = COLOR_SECONDARY
        rt = p.add_run(text)
        rt.font.name = "Calibri"
        rt.font.size = Pt(11)
        rt.font.color.rgb = COLOR_SECONDARY
        return p

    # =========================================================================
    # 1. ГЛАВНАЯ ИДЕЯ ПРОЕКТА
    # =========================================================================
    add_h1("1. Главная идея исследовательского проекта")

    add_p(
        "Исследование направлено на преодоление фундаментального противоречия в системе образования Кыргызской Республики: "
        "более чем за 20 лет проведения Общереспубликанского тестирования (ОРТ, с 2002 по 2026 гг.) накоплен колоссальный массив данных "
        "об образовательных достижениях (~1 млн абитуриентов), однако эти сведения оставались фрагментированными в сотнях разрозненных PDF-отчетов "
        "и никогда не исследовались как непрерывный пространственно-временной панельный процесс во взаимосвязи с региональным социально-экономическим контекстом.",
        bold_prefix="Суть проблемы: "
    )

    add_p(
        "Сформировать верифицированный 20-летний пространственно-временной датасет результатов ОРТ (2006–2025 гг.) по всем 48 районам и городам Кыргызстана, "
        "интегрировать его с показателями Нацстаткома и геоданными, выявить ключевые нелинейные драйверы академической успешности с помощью методов машинного обучения (CatBoost/LightGBM) "
        "и Explainable AI (SHAP), и разработать прототип Системы поддержки принятия решений (DSS) со сценарным модулем What-If для доказательной образовательной политики.",
        bold_prefix="Главная цель работы: "
    )

    add_p(
        "результаты Общереспубликанского тестирования абитуриентов Кыргызской Республики за 20-летний период (2006–2025 гг.).",
        bold_prefix="Объект исследования: "
    )
    add_p(
        "пространственно-временные закономерности, структурные разрывы (Бишкек — регионы, город — село) и зависимость образовательных результатов "
        "от социально-экономических, инфраструктурных и кадровых характеристик административных территорий.",
        bold_prefix="Предмет исследования: "
    )

    add_h2("Ключевые исследовательские вопросы (Research Questions):")
    add_bullet("RQ1 (Spatial Inequality):", "Как эволюционировали региональные и сельско-городские разрывы в результатах ОРТ в 2006–2025 гг.? Наблюдается ли конвергенция (сближение) регионов или консервация отставания?")
    add_bullet("RQ2 (Predictive Determinants):", "Какие социально-экономические и институциональные факторы (нагрузка на учителя, уровень зарплат, квалификация кадров, уровень бедности) вносят наибольший вклад в вариацию баллов ОРТ согласно интерпретируемым моделям машинного обучения?")
    add_bullet("RQ3 (Model Generalization):", "Насколько алгоритмы машинного обучения способны обобщаться между географическими макрозонами (Север vs Юг) и временными горизонтами (прогноз на будущее без деградации качества)?")

    # =========================================================================
    # 2. МЕЖДУНАРОДНЫЕ АНАЛОГИ
    # =========================================================================
    add_h1("2. Аналогичные работы в мире и какие проблемы они решают")

    add_p(
        "В мировой науке интеграция результатов стандартизированных тестов с методами пространственного анализа, машинного обучения и Explainable AI "
        "является признанным золотым стандартом для доказательной образовательной политики (Evidence-Based Policy). "
        "Существует ряд крупнейших национальных и международных прецедентов:"
    )

    # Comparison Table
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Проект / Экзамен", "Страна", "Применяемые методы", "Какую проблему решает"]
    col_widths = [Inches(1.8), Inches(1.1), Inches(2.2), Inches(2.4)]

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.name = "Calibri"
        hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(10)
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hdr_cells[i], "1E3A8A")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)

    analogs_data = [
        ("SEDA / SAT & ACT\n(Stanford University)", "США", "Spatio-Temporal Panel, GIS, OLS/Hierarchical Models", "Разделение вклада качества школы и фоновой бедности района; карта образовательных возможностей (Opportunity Atlas)."),
        ("ENEM\n(INEP Microdata)", "Бразилия", "XGBoost, Random Forest, SHAP, Deep Learning", "Оценка 'Opportunity Gap' между Севером и Югом; поиск нелинейных порогов влияния дохода семей на поступление в вузы."),
        ("Saber 11\n(ICFES)", "Колумбия", "Causal ML, Random Forest, Regression Discontinuity", "Оценка добавленной стоимости школ (School Value-Added) и прогноз риска образовательного отсева (Dropout Risk)."),
        ("PISA / TIMSS\n(OECD Datasets)", "Международные (80+ стран)", "CatBoost, LightGBM, SHAP, Causal Trees", "Выявление роли цифровизации и учительской нагрузки в развивающихся странах; оценка отдачи от инвестиций в образование."),
        ("ЕНТ (UNT)\n(НЦТ РК)", "Казахстан", "Статистический анализ, регрессионное моделирование", "Анализ структурного отставания сельских малокомплектных школ от элитных городских лицеев (НИШ, БИЛ).")
    ]

    for row_data in analogs_data:
        row_cells = table.add_row().cells
        for i, val in enumerate(row_data):
            row_cells[i].text = val
            row_cells[i].paragraphs[0].runs[0].font.name = "Calibri"
            row_cells[i].paragraphs[0].runs[0].font.size = Pt(9.5)
            row_cells[i].paragraphs[0].runs[0].font.color.rgb = COLOR_SECONDARY
            set_cell_background(row_cells[i], "F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_margins(row_cells[i], top=100, bottom=100, left=120, right=120)

    doc.add_paragraph().paragraph_format.space_before = Pt(6)

    add_h2("Какие общие проблемы решают эти мировые проекты:")
    add_bullet("1. Преодоление 'черного ящика' (Black-Box Explainability):", "Вместо непрозрачных предсказаний SHAP-анализ показывает чиновникам, какой именно фактор (зарплата, нагрузка, квалификация) перевесил в прогнозе для конкретного региона.")
    add_bullet("2. Устранение эффекта ложной корреляции (Confounding):", "Школы в богатых мегаполисах кажутся успешными не потому, что лучше учат, а из-за благосостояния родителей. Модели позволяют вычесть фактор богатства и оценить реальный вклад школы.")
    add_bullet("3. Выявление критических точек перегиба (Tipping Points):", "Определение порогов, после которых вливание ресурсов перестает давать отдачу (закон убывающей предельной доходности в образовании).")

    # =========================================================================
    # 3. В ЧЕМ СПЕЦИФИКА И ОТЛИЧИЯ НАШЕГО ИССЛЕДОВАНИЯ
    # =========================================================================
    add_h1("3. Что в нашем случае будет отличаться (Научная новизна)")

    add_p(
        "Наш проект не копирует зарубежные работы, а адаптирует передовой мировой стек под уникальную географическую, "
        "институциональную и историческую специфику Кыргызстана. Ключевые отличия проекта EduAnalytics-KG:"
    )

    add_bullet("1. Первый 20-летний временной ряд в Центральной Азии (2006–2025):", 
               "Большинство мировых статей используют статичный срез за 1–2 года. Мы собрали беспрецедентную панель за 17 лет непрерывных наблюдений (760 район-лет), "
               "что позволяет исследовать эволюцию неравенства на дистанции целого поколения в постсоветской переходной экономике.")

    add_bullet("2. Специфика высокогорной и изолированной географии:", 
               "В отличие от равнинных регионов США или Бразилии, Кыргызстан обладает экстремальным рельефом (94% гор, перевалы, анклавы в Баткене, отдаленные долины Нарына). "
               "Мы напрямую исследуем, как фактор физической изоляции и особый высокогорный статус школ влияют на академическую успешность и дефицит кадров.")

    add_bullet("3. Строгое разделение корреляции, предикции и причинности:", 
               "В проекте вводится жесткий методологический запрет на выдачу предсказательных связей за причинные эффекты. "
               "Мы тестируем модель на Out-of-Distribution (OOD) обобщаемость: способна ли модель, обученная на северных областях, точно предсказывать результаты южных?")

    add_bullet("4. Создание рабочего прикладного инструмента — DSS с What-If модулем:", 
               "Академические статьи обычно завершаются таблицей коэффициентов. Наш проект доводит моделирование до интерактивного прототипа веб-сервиса (Decision Support System), "
               "где образовательный аналитик может передвинуть ползунок ресурсов района и увидеть модельный отклик.")

    # =========================================================================
    # 4. ЧТО НУЖНО ПОКАЗАТЬ И ДОКАЗАТЬ В РАБОТЕ
    # =========================================================================
    add_h1("4. Что конкретно нужно показать и доказать в работе (Структура результатов)")

    add_p("В итоговом тексте статьи/диссертации должны быть представлены 5 конкретных доказательных блоков:")

    add_bullet("Блок 1. Пространственно-временная картография и тренды (RQ1):", 
               "• Карты распределения баллов ОРТ по 48 районам КР в динамике (2006 vs 2015 vs 2025).\n"
               "• Проверка гипотезы конвергенции: сократился ли разрыв между Бишкеком и регионами за 20 лет? (Индекс Джини и коэффициент вариации баллов во времени).")

    add_bullet("Блок 2. Сравнительный бенчмарк моделей машинного обучения (ML Benchmark):", 
               "• Сравнение эконометрических моделей (Panel OLS, Fixed Effects) с алгоритмами градиентного бустинга (CatBoost, LightGBM, Random Forest).\n"
               "• Метрики качества: MAE, RMSE, R² на пространственном и временном hold-out.")

    add_bullet("Блок 3. Интерпретация факторов успеха через SHAP (RQ2):", 
               "• SHAP Beeswarm Plot: ранжирование вклада факторов (нагрузка на учителя, региональная зарплата, урбанизация, обеспеченность кадрами).\n"
               "• SHAP Dependence Plots: выявление нелинейных порогов (при каком значении нагрузки на учителя результаты начинают падать).")

    add_bullet("Блок 4. Феномен 'Позитивных девиантов' (Positive Deviance, E8):", 
               "• Статистический анализ остатков: выявление районов, которые стабильно показывают результат выше модельного ожидания при неблагоприятных ресурсах.\n"
               "• Формирование практических гипотез о локальных педагогических практиках этих районов для масштабирования.")

    add_bullet("Блок 5. Прототип системы поддержки принятия решений (DSS What-If):", 
               "• Демонстрация интерактивного модуля сценарного анализа: выбор района -> изменение управляемых параметров (нагрузка, кадры) -> модельная оценка изменения баллов и вероятности преодоления порогового балла (110).")

    # =========================================================================
    # 5. ТЕКУЩИЙ ЗАДЕЛ И ГОТОВНОСТЬ ПРОЕКТА
    # =========================================================================
    add_h1("5. Текущий задел и готовность проекта (Уже выполнено)")

    add_p(
        "Проект находится не на стадии абстрактной идеи, а имеет полностью развернутый Data Engineering фундамент:",
        bold_prefix="Текущий статус: "
    )

    add_bullet("Собраны первоисточники:", "Автоматически скачаны и каталогизированы 20 официальных годовых аналитических сборников ЦООМО (2006–2025 гг., >100 МБ PDF).")
    add_bullet("Построена пространственная витрина:", "Сформирован проверенный панельный датасет по 48 районам и городам Кыргызстана за 17 лет (760 записей, 16 признаков) в форматах CSV и Apache Parquet.")
    add_bullet("Интегрированы геоданные:", "Загружены и привязаны официальные векторные границы районов и областей КР (GeoJSON ADM1 и ADM2).")
    add_bullet("Создан мастер-реестр территорий:", "Разработан справочник сопоставления всех районов с официальными кодами СОАТО Нацстаткома КР.")

    add_p(
        "Таким образом, все эмпирические данные полностью готовы к обучению моделей машинного обучения, расчету SHAP-значений и формированию финальных научных визуализаций.",
        bold_prefix="Вывод: "
    )

    # Save Document
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"✓ Document saved successfully to {output_path}")

if __name__ == "__main__":
    out_file = Path("EduAnalytics_KG_Research_Proposal.docx")
    create_document(out_file)
