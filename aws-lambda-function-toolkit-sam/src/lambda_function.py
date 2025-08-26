import os
import io
import json
import logging
from typing import Optional

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Basic structured logger
log = logging.getLogger(__name__)
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def _parse_csv_from_sqs_event(event: dict) -> Optional[str]:
    """
    Try to extract a CSV string from SQS event. We accept either a raw CSV in body
    OR a JSON string with a 'csv' key.
    """
    try:
        records = event.get("Records", [])
        for rec in records:
            body = rec.get("body", "")
            # Try JSON first
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict) and "csv" in parsed:
                    return str(parsed["csv"])
            except json.JSONDecodeError:
                pass
            # Fallback: if it looks like CSV (has commas and newlines), just return
            if "," in body and ("\n" in body or "\r\n" in body):
                return body
    except Exception as e:
        log.exception("Failed to parse SQS event body: %s", e)
    return None

def _build_sample_dataframe() -> pd.DataFrame:
    data = [
        {"Invoice": "INV-1001", "Customer": "Acme Corp", "Amount": 1234.56},
        {"Invoice": "INV-1002", "Customer": "Globex", "Amount": 789.01},
        {"Invoice": "INV-1003", "Customer": "Soylent", "Amount": 2345.00},
    ]
    return pd.DataFrame(data)

def _df_to_table(df: pd.DataFrame) -> Table:
    # Convert DataFrame to list-of-lists (strings)
    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightyellow]),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    return table

def _write_pdf(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Sample DataFrame Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Rows: {len(df)} | Columns: {len(df.columns)}", styles["Normal"]),
        Spacer(1, 12),
        _df_to_table(df),
    ]
    doc.build(story)

def lambda_handler(event, context):
    """
    - Accepts an SQS event.
    - Tries to read CSV from message body (raw CSV or JSON with 'csv' key).
    - If absent, uses a built-in sample CSV.
    - Builds a pandas DataFrame, writes a PDF using reportlab.
    - Returns the output path (inside the container) for verification.
    """
    try:
        log.info("Lambda started")
        log.info("RequestId=%s", getattr(context, "aws_request_id", "local"))

        output_dir = os.getenv("OUTPUT_DIR", "/tmp")
        pdf_name = "sample_dataframe.pdf"
        out_path = os.path.join(output_dir, pdf_name)

        csv_str = _parse_csv_from_sqs_event(event)
        if csv_str:
            log.info("CSV found in SQS message")
            df = pd.read_csv(io.StringIO(csv_str))
        else:
            log.info("No CSV in event; using built-in sample data")
            df = _build_sample_dataframe()

        _write_pdf(df, out_path)
        log.info("PDF written to %s", out_path)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "OK", "pdf_path": out_path, "rows": int(len(df))}),
        }
    except Exception as e:
        log.exception("Processing failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
