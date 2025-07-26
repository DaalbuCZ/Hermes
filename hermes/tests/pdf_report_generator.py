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
from .models import TestResult


def get_best_test_scores(person, active_test, team):
    test_results = TestResult.objects.filter(
        person=person, active_test=active_test, team=team
    )
    if not test_results:
        return None

    return {
        "Ladder": max(
            (r.ladder_score for r in test_results if r.ladder_score is not None),
            default=None,
        ),
        "Hexagon": max(
            (r.hexagon_score for r in test_results if r.hexagon_score is not None),
            default=None,
        ),
        "Y-Test": max(
            (r.y_test_score for r in test_results if r.y_test_score is not None),
            default=None,
        ),
        "Brace": max(
            (r.brace_score for r in test_results if r.brace_score is not None),
            default=None,
        ),
        "Medicimbal": max(
            (
                r.medicimbal_score
                for r in test_results
                if r.medicimbal_score is not None
            ),
            default=None,
        ),
        "Jet": max(
            (r.jet_score for r in test_results if r.jet_score is not None), default=None
        ),
        "Triple Jump": max(
            (
                r.triple_jump_score
                for r in test_results
                if r.triple_jump_score is not None
            ),
            default=None,
        ),
        "Beep Test": max(
            (r.beep_test_score for r in test_results if r.beep_test_score is not None),
            default=None,
        ),
    }


def generate_test_results_pdf(test_results, output, adjudicator):
    # Handle single test result case
    if not isinstance(test_results, (list, tuple)):
        test_results = [test_results]

    # Filter test results for people in adjudicator's teams
    adjudicator_teams = adjudicator.teams.all()
    test_results = [tr for tr in test_results if tr.person.team in adjudicator_teams]

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

    # Add Best Results section at the beginning
    story.append(Paragraph("Team Best Results", title_style))
    story.append(Spacer(1, 12))

    # Create best results table
    best_results_data = [
        [
            "Name",
            "Ladder",
            "Hexagon",
            "Y-Test",
            "Brace",
            "Medicimbal",
            "Jet",
            "Triple Jump",
            "Beep Test",
        ],
    ]

    # Get unique people and active test from filtered test results
    people = {result.person for result in test_results}
    active_test = test_results[0].active_test if test_results else None

    for person in people:
        best_scores = get_best_test_scores(person, active_test, person.team)
        if best_scores:
            best_results_data.append(
                [
                    person.full_name,
                    (
                        str(best_scores["Ladder"])
                        if best_scores["Ladder"] is not None
                        else "-"
                    ),
                    (
                        str(best_scores["Hexagon"])
                        if best_scores["Hexagon"] is not None
                        else "-"
                    ),
                    (
                        str(best_scores["Y-Test"])
                        if best_scores["Y-Test"] is not None
                        else "-"
                    ),
                    (
                        str(best_scores["Brace"])
                        if best_scores["Brace"] is not None
                        else "-"
                    ),
                    (
                        str(best_scores["Medicimbal"])
                        if best_scores["Medicimbal"] is not None
                        else "-"
                    ),
                    str(best_scores["Jet"]) if best_scores["Jet"] is not None else "-",
                    (
                        str(best_scores["Triple Jump"])
                        if best_scores["Triple Jump"] is not None
                        else "-"
                    ),
                    (
                        str(best_scores["Beep Test"])
                        if best_scores["Beep Test"] is not None
                        else "-"
                    ),
                ]
            )

    # Calculate column widths to fit the page
    name_width = 2 * inch
    score_width = 0.75 * inch
    total_width = 8 * score_width + name_width

    best_table = Table(best_results_data, colWidths=[name_width] + [score_width] * 8)
    best_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(best_table)
    story.append(PageBreak())

    for test_result in test_results:
        # Add title for each person
        story.append(
            Paragraph(f"Test Results for {test_result.person.full_name}", title_style)
        )
        story.append(Spacer(1, 12))

        # Get the last 3 test results for this person
        last_three_results = list(
            TestResult.objects.filter(
                person=test_result.person,
                active_test=test_result.active_test,
                team=test_result.team,
            ).order_by("-test_date")[:3]
        )

        # Ensure current test result is included and first in the list
        if test_result not in last_three_results:
            last_three_results = [test_result] + list(last_three_results[:2])
        else:
            last_three_results.remove(test_result)
            last_three_results.insert(0, test_result)

        # Historical results are all except the current one
        historical_results = last_three_results[1:]

        # Create table data with dates as columns
        data = [
            ["Category"]
            + [result.test_date.strftime("%Y-%m-%d") for result in last_three_results],
        ]

        # Add scores for each category
        categories = [
            ("Strength Score", "strength_score"),
            ("Speed Score", "speed_score"),
            ("Endurance Score", "endurance_score"),
            ("Agility Score", "agility_score"),
        ]

        for category_name, field_name in categories:
            row = [category_name]
            for result in last_three_results:
                score = getattr(result, field_name)
                row.append(f"{score:.1f}" if score is not None else "-")
            data.append(row)

        # Create table with equal column widths
        num_columns = len(last_three_results) + 1  # +1 for category column
        column_width = 7.5 * inch / num_columns
        table = Table(data, colWidths=[column_width] * num_columns)

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

        # Get historical results from the last three results for the radar plot
        radar_buffer = generate_radar_plot_from_scores(
            test_result.speed_score or 0,
            test_result.endurance_score or 0,
            test_result.agility_score or 0,
            test_result.strength_score or 0,
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

        # Add page break between people (except for the last one)
        if test_result != test_results[-1]:
            story.append(PageBreak())

    # Build PDF
    doc.build(story)
