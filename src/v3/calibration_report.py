from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


def generate_calibration_report(
    instrument,
    record,
    statistics
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    heading_style = styles["Heading2"]

    normal_style = styles["BodyText"]

    result_style = ParagraphStyle(
        "Result",
        parent=styles["Heading2"],
        alignment=1,
        fontSize=18,
        spaceAfter=12
    )

    story = []

    # ------------------------------------------
    # TITLE
    # ------------------------------------------

    story.append(
        Paragraph(
            "LAB CALIBRATION REPORT",
            title_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Lab Calibration System V3",
            normal_style
        )
    )

    story.append(
        Spacer(1, 18)
    )


    # ------------------------------------------
    # REPORT INFORMATION
    # ------------------------------------------

    story.append(
        Paragraph(
            "Report Information",
            heading_style
        )
    )

    report_data = [
        ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Calibration Record ID", str(record.record_id)],
        ["Model Version", record.model_version],
        ["Measurement Time", str(record.measurement_time)]
    ]

    report_table = Table(
        report_data,
        colWidths=[55 * mm, 115 * mm]
    )

    report_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(report_table)

    story.append(
        Spacer(1, 18)
    )


    # ------------------------------------------
    # INSTRUMENT INFORMATION
    # ------------------------------------------

    story.append(
        Paragraph(
            "Instrument Information",
            heading_style
        )
    )

    instrument_data = [
        ["Name", instrument.name],
        ["Manufacturer", instrument.manufacturer],
        ["Model", instrument.model],
        ["Serial Number", instrument.serial_number],
        ["Instrument Type", instrument.instrument_type],
        ["Instrument Status", instrument.status]
    ]

    instrument_table = Table(
        instrument_data,
        colWidths=[55 * mm, 115 * mm]
    )

    instrument_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(instrument_table)

    story.append(
        Spacer(1, 18)
    )


    # ------------------------------------------
    # CALIBRATION RESULT
    # ------------------------------------------

    story.append(
        Paragraph(
            "Calibration Result",
            heading_style
        )
    )

    result_data = [
        ["Estimated CO", f"{record.estimated_value:.4f}"],
        ["Reference CO", f"{record.reference_value:.4f}"],
        ["Error", f"{record.error:+.4f}"],
        ["Tolerance", f"±{record.tolerance:.4f}"],
        ["Status", record.status]
    ]

    result_table = Table(
        result_data,
        colWidths=[55 * mm, 115 * mm]
    )

    result_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(result_table)

    story.append(
        Spacer(1, 12)
    )


    # ------------------------------------------
    # PASS / FAIL
    # ------------------------------------------

    if record.status == "PASS":

        result_text = "CALIBRATION PASS"

    else:

        result_text = "CALIBRATION FAIL"


    story.append(
        Paragraph(
            result_text,
            result_style
        )
    )

    story.append(
        Spacer(1, 8)
    )


    # ------------------------------------------
    # STATISTICS
    # ------------------------------------------

    if statistics:

        story.append(
            Paragraph(
                "Calibration Statistics",
                heading_style
            )
        )

        statistics_data = [
            ["Total Calibrations", str(statistics["count"])],
            ["PASS", str(statistics["pass_count"])],
            ["FAIL", str(statistics["fail_count"])],
            ["Pass Rate", f'{statistics["pass_rate"]:.1f}%'],
            ["Mean Absolute Error", f'{statistics["mae"]:.4f}'],
            ["Average Error", f'{statistics["average_error"]:+.4f}'],
            [
                "Maximum Absolute Error",
                f'{statistics["maximum_absolute_error"]:.4f}'
            ]
        ]

        statistics_table = Table(
            statistics_data,
            colWidths=[80 * mm, 90 * mm]
        )

        statistics_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        story.append(
            statistics_table
        )


    story.append(
        Spacer(1, 24)
    )


    # ------------------------------------------
    # FOOTER
    # ------------------------------------------

    story.append(
        Paragraph(
            "Generated by Lab Calibration System V3",
            normal_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()