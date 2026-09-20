import json
import re
from pathlib import Path

import pandas as pd


def normalize_amount(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace("$", "").replace("€", "").replace("£", "").replace(" ", "")
    if not text:
        return None
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        if len(parts[-1]) in (1, 2):
            text = "".join(parts[:-1]) + "." + parts[-1]
        else:
            text = text.replace(",", "")
    try:
        return round(float(text), 2)
    except ValueError:
        return None


def extract_fields(ocr_text: str) -> dict:
    result = {
        "invoice_number": None,
        "invoice_date": None,
        "net_total": None,
        "tax": None,
        "gross_total": None,
    }

    number_match = re.search(r"Invoice\s*no:\s*([A-Za-z0-9\-]+)", ocr_text, flags=re.I)
    if number_match:
        result["invoice_number"] = number_match.group(1).strip()

    date_match = re.search(
        r"Date\s+of\s+issue:\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})",
        ocr_text,
        flags=re.I,
    )
    if date_match:
        result["invoice_date"] = date_match.group(1).strip()

    total_match = re.search(r"\bTotal\b\s*(.*)$", ocr_text, flags=re.I)
    if total_match:
        amount_tokens = re.findall(
            r"(?<!\d)(\d{1,3}(?:[ \.,]\d{3})*[.,]\d{2}|\d+[.,]\d{2})(?!\d)",
            total_match.group(1),
        )
        values = [normalize_amount(token) for token in amount_tokens]
        if len(values) >= 3:
            result["net_total"], result["tax"], result["gross_total"] = values[-3:]

    return result


def load_invoice_batches(paths):
    frames = [pd.read_csv(path) for path in paths]
    return pd.concat(frames, ignore_index=True)


def parse_annotation(raw_json: str) -> dict:
    return json.loads(raw_json)


def benchmark(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows = []
    for _, row in df.iterrows():
        annotation = parse_annotation(row["Json Data"])
        extracted = extract_fields(row["OCRed Text"])

        gt_number = str(annotation["invoice"]["invoice_number"]).strip()
        gt_date = str(annotation["invoice"]["invoice_date"]).strip()
        gt_tax = normalize_amount(annotation["subtotal"]["tax"])
        annotated_total = normalize_amount(annotation["subtotal"]["total"])

        if annotated_total == extracted["gross_total"]:
            total_semantics = "gross"
        elif annotated_total == extracted["net_total"]:
            total_semantics = "net"
        else:
            total_semantics = "other"

        rows.append(
            {
                "file_name": row["File Name"],
                "invoice_number_gt": gt_number,
                "invoice_number_pred": extracted["invoice_number"],
                "invoice_number_match": gt_number == extracted["invoice_number"],
                "invoice_date_gt": gt_date,
                "invoice_date_pred": extracted["invoice_date"],
                "invoice_date_match": gt_date == extracted["invoice_date"],
                "tax_gt": gt_tax,
                "tax_pred": extracted["tax"],
                "tax_match": None if gt_tax is None else gt_tax == extracted["tax"],
                "annotated_total": annotated_total,
                "extracted_net_total": extracted["net_total"],
                "extracted_gross_total": extracted["gross_total"],
                "total_annotation_semantics": total_semantics,
                "total_reconciled": total_semantics in {"net", "gross"},
            }
        )

    results = pd.DataFrame(rows)
    metrics = {
        "records": int(len(results)),
        "unique_files": int(df["File Name"].nunique()),
        "duplicate_rows": int(df.duplicated().sum()),
        "invoice_number_exact_match": float(results["invoice_number_match"].mean()),
        "invoice_date_exact_match": float(results["invoice_date_match"].mean()),
        "tax_exact_match_nonmissing": float(results["tax_match"].dropna().mean()),
        "tax_missing_annotations": int(results["tax_match"].isna().sum()),
        "total_reconciliation_rate": float(results["total_reconciled"].mean()),
        "total_annotation_gross_count": int((results["total_annotation_semantics"] == "gross").sum()),
        "total_annotation_net_count": int((results["total_annotation_semantics"] == "net").sum()),
    }
    return results, metrics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="+", help="Invoice CSV batch files")
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    output_dir = Path(args.results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_invoice_batches(args.csv)
    results, metrics = benchmark(data)
    results.to_csv(output_dir / "field_benchmark.csv", index=False)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
