import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Регистрируем кириллический шрифт ---
font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))


def _make_table(rows):
    """Вспомогательная функция для создания таблицы"""
    data = [["#", "Тип авто", "Интервал, мин", "Время прибытия", "Время выезда", "Секция"]]
    for i, row in enumerate(rows, start=1):
        data.append([
            i, row["car_type"], row["interval"],
            row["arrival_time"], row["departure_time"], row["section"]
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # кириллица
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return table


def generate_pdf_report(schedule_unregulated, schedule_regulated, metrics, graph_paths, output_dir):
    pdf_path = os.path.join(output_dir, "report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    for style_name in styles.byName:
        styles[style_name].fontName = "DejaVuSans"

    # --- Заголовок ---
    story.append(Paragraph("Отчет по моделированию мультимодальной транспортной системы", styles["Title"]))
    story.append(Spacer(1, 12))

    # --- Нерегулируемый поток ---
    story.append(Paragraph("<b>Нерегулируемый поток</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))
    story.append(_make_table(schedule_unregulated))
    story.append(Spacer(1, 12))

    # --- Регулируемый поток ---
    story.append(Paragraph("<b>Регулируемый поток</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))
    story.append(_make_table(schedule_regulated))
    story.append(Spacer(1, 12))

    # --- Итоговые показатели ---
    story.append(Paragraph("<b>Итоговые показатели</b>", styles["Heading2"]))
    story.append(Paragraph(f"Среднее время обслуживания: {metrics['avg_service_time']} мин", styles["Normal"]))
    story.append(Paragraph(f"Средний простой: {metrics['avg_idle_time']} мин", styles["Normal"]))
    story.append(Paragraph(f"Суммарные затраты: {metrics['total_cost']} руб", styles["Normal"]))
    story.append(Spacer(1, 12))
    if "economic_effect" in metrics:
        story.append(Paragraph(f"Экономический эффект (сокращение потерь): +{metrics['economic_effect']} руб", styles["Normal"]))



    # --- Графики ---
    if isinstance(graph_paths, dict):
        graph_list = list(graph_paths.values())
    else:
        graph_list = graph_paths

    if graph_list:
        story.append(Paragraph("<b>Графики моделирования</b>", styles["Heading2"]))
        for path in graph_list:
            img_path = os.path.abspath(path)
            if not os.path.exists(img_path):
                print(f"[!] Не найден файл графика: {img_path}")
                continue
            story.append(Image(img_path, width=16 * cm, height=9 * cm))
            story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_path
