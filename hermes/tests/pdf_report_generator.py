from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image,
    Spacer,
    PageBreak,
)
from io import BytesIO
from .radarplot_generator import generate_radar_plot_from_scores
from PIL import Image as PILImage


def generate_test_results_pdf(test_results, output):
    """
    Generate a PDF report containing test results and radar plots for multiple profiles

    Parameters:
    -----------
    test_results : list of TestResult or single TestResult
        The test result object(s) containing all scores
    output : str or BytesIO
        Path where the PDF should be saved or a BytesIO object to write to
    """
    # Handle single test result case
    if not isinstance(test_results, (list, tuple)):
        test_results = [test_results]

    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Prepare the story (content) for the PDF
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30
    )

    for test_result in test_results:
        # Add title for each person
        story.append(
            Paragraph(f"Test Results for {test_result.profile.full_name}", title_style)
        )
        story.append(Spacer(1, 12))

        # Create table data
        data = [
            ["Category", "Score", "Previous", "Change"],
        ]

        # Get previous test result for comparison
        previous_results = test_result.profile.get_last_three_test_results()
        previous_result = previous_results[1] if len(previous_results) > 1 else None

        def format_change(current, previous):
            if previous is None:
                return "-"
            change = current - previous
            return f"{change:+.1f}" if change != 0 else "0.0"

        # Add scores with comparison
        categories = [
            ("Strength Score", test_result.strength_score),
            ("Speed Score", test_result.speed_score),
            ("Endurance Score", test_result.endurance_score),
            ("Agility Score", test_result.agility_score),
        ]

        for category, current_score in categories:
            prev_score = (
                getattr(previous_result, category.lower().replace(" ", "_"), None)
                if previous_result
                else None
            )
            data.append(
                [
                    category,
                    f"{current_score:.1f}",
                    f"{prev_score:.1f}" if prev_score is not None else "-",
                    format_change(current_score, prev_score),
                ]
            )

        # Create table
        table = Table(data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 30))

        # Get historical results (excluding the current one)
        historical_results = list(previous_results[1:])

        # Generate and add radar plot
        radar_buffer = generate_radar_plot_from_scores(
            test_result.speed_score,
            test_result.endurance_score,
            test_result.agility_score,
            test_result.strength_score,
            historical_results=historical_results,
        )

        # Convert PNG to JPG (reduces file size)
        pil_image = PILImage.open(radar_buffer)
        jpg_buffer = BytesIO()
        pil_image.convert("RGB").save(jpg_buffer, format="JPEG", quality=95)
        jpg_buffer.seek(0)

        # Add radar plot to PDF
        img = Image(jpg_buffer, width=7 * inch, height=6 * inch)
        story.append(img)

        # Add page break between profiles (except for the last one)
        if test_result != test_results[-1]:
            story.append(PageBreak())

    # Build PDF
    doc.build(story)
