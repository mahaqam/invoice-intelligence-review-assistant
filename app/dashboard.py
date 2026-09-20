import streamlit as st

from src.invoice_parser import extract_fields

st.set_page_config(page_title="Invoice Intelligence Review", layout="wide")
st.title("Invoice Intelligence & Review Assistant")
st.write("Paste OCR text from an invoice to review extracted structured fields.")

ocr_text = st.text_area("OCR text", height=280)
if st.button("Extract fields", type="primary"):
    if not ocr_text.strip():
        st.warning("Paste OCR text first.")
    else:
        fields = extract_fields(ocr_text)
        st.subheader("Extracted fields")
        st.json(fields)
