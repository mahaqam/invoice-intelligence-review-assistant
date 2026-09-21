# Invoice Intelligence & Review Assistant

Internal document-intelligence prototype for extracting structured fields from OCR text, validating invoice annotations, exposing extraction through a REST API, and reviewing results in a polished Streamlit interface.

## Live demo
**Try the interactive app:** https://invoice-intelligence-review-assistant.streamlit.app/

The interface includes:
- a built-in sample invoice
- editable OCR-text input
- structured invoice-field output
- benchmark metrics and project scope
- limitations and a direct GitHub link

## Dataset
The analysis used three uploaded invoice CSV batches containing **1,414 rows** with file names, JSON annotations, and OCR text. There were **1,413 unique file names** and one duplicate row.

## What I built
- Parsed OCR text into structured invoice fields: invoice number, issue date, net total, tax, and gross total.
- Normalized locale-style numeric formats such as `1 025,61` and `232.95`.
- Benchmarked extracted values against the supplied JSON annotations.
- Added a data-quality check for inconsistent annotation semantics.
- Added a FastAPI endpoint and a recruiter-friendly Streamlit review interface.

## Verified results
- Invoice number exact match: **100.0%**
- Invoice date exact match: **100.0%**
- Tax exact match on non-missing annotations: **100.0%**
- Annotated total reconciled to an extracted printed net or gross total: **100.0%**
- Data validation identified **28 rows** where the JSON `subtotal.total` represented net total rather than gross total, plus **4 missing tax annotations**.

The total metric is a reconciliation metric, not a claim that the dataset's total label had one consistent meaning.

## Run locally
```bash
pip install -r requirements.txt
python src/invoice_parser.py batch1_1.csv batch1_2.csv batch1_3.csv
uvicorn api.app:app --reload
streamlit run app/dashboard.py
```

## Repository structure
- `src/invoice_parser.py` — extraction, normalization, validation, benchmark
- `api/app.py` — REST extraction endpoint
- `app/dashboard.py` — interactive review UI
- `.streamlit/config.toml` — Streamlit theme/deployment configuration
- `results/metrics.json` — verified benchmark summary
- `results/annotation_summary.csv` — annotation-semantics QA summary

## Deployment
- Streamlit entry point: `app/dashboard.py`
- Branch: `main`
- No dataset upload or secrets are required for the interactive parser demo.

## Limitations
- The provided files contain OCR text rather than original invoice images, so this project benchmarks **post-OCR document parsing**, not OCR-engine accuracy.
- The parser is tuned to the invoice layout represented in this dataset.
- Production document intelligence would need layout variation, image-quality testing, confidence handling, privacy controls, and human-review thresholds.
