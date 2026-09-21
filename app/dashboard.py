from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.invoice_parser import extract_fields

SAMPLE_OCR = """Invoice no: INV-2026-1042
Date of issue: 18/09/2026
Supplier: Atlas Business Services
Customer: Northstar Operations

Description        Qty      Price      Amount
Consulting           1     950.00      950.00
Support              1      75.00       75.00

Total 1 025,00 51,25 1 076,25
"""

st.set_page_config(
    page_title="Invoice Intelligence & Review Assistant",
    page_icon="🧾",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: rgba(127,127,127,.08); margin-bottom: 1rem;}
    .hero h1 {margin: 0 0 .35rem 0;}
    .muted {opacity: .78;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🧾 Invoice Intelligence & Review Assistant</h1>
      <div class="muted">A portfolio prototype that turns post-OCR invoice text into structured fields for review.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
m1.metric("Benchmark records", "1,414")
m2.metric("Field reconciliation", "100%")
m3.metric("Data-quality flags", "28")

st.caption(
    "The uploaded benchmark data already contained OCR text, so this demo evaluates parsing and validation rather than OCR-engine accuracy."
)

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Try the parser")
    if "invoice_text" not in st.session_state:
        st.session_state.invoice_text = SAMPLE_OCR

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load sample", use_container_width=True):
            st.session_state.invoice_text = SAMPLE_OCR
    with c2:
        if st.button("Clear", use_container_width=True):
            st.session_state.invoice_text = ""

    ocr_text = st.text_area(
        "Invoice OCR text",
        key="invoice_text",
        height=330,
        help="Paste text produced by an OCR system. The parser looks for invoice number, issue date, and total fields.",
    )

    run = st.button("Extract structured fields", type="primary", use_container_width=True)

with right:
    st.subheader("Structured output")
    if run:
        if not ocr_text.strip():
            st.warning("Paste invoice OCR text first.")
        else:
            fields = extract_fields(ocr_text)
            found = sum(value is not None for value in fields.values())
            st.success(f"Extracted {found} of {len(fields)} target fields")

            labels = {
                "invoice_number": "Invoice number",
                "invoice_date": "Issue date",
                "net_total": "Net total",
                "tax": "Tax",
                "gross_total": "Gross total",
            }
            for key, label in labels.items():
                value = fields.get(key)
                st.text_input(label, "Not found" if value is None else str(value), disabled=True)

            with st.expander("Raw JSON output"):
                st.json(fields)
    else:
        st.info("Use the sample invoice or paste your own OCR text, then run the parser.")

st.divider()
st.subheader("What this project demonstrates")
col1, col2, col3 = st.columns(3)
col1.markdown("**Document intelligence**\n\nRegex/JSON parsing and numeric normalization over invoice text.")
col2.markdown("**Validation**\n\nField-level benchmarking, duplicate checks, and annotation-semantic review.")
col3.markdown("**Application layer**\n\nA Streamlit review UI plus a separate FastAPI endpoint in the repository.")

with st.expander("Scope & limitations"):
    st.write(
        "This is a portfolio prototype, not a production deployment. It assumes invoice layouts similar to the benchmark data. "
        "A production system would need original-image OCR testing, layout variation, confidence thresholds, privacy controls, monitoring, and human fallback."
    )

st.link_button(
    "View source on GitHub",
    "https://github.com/mahaqam/invoice-intelligence-review-assistant",
    use_container_width=True,
)
