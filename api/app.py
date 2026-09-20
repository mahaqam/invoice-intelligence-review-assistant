from fastapi import FastAPI
from pydantic import BaseModel

from src.invoice_parser import extract_fields

app = FastAPI(title="Invoice Intelligence API")


class InvoiceOCRRequest(BaseModel):
    ocr_text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
def extract(request: InvoiceOCRRequest):
    return extract_fields(request.ocr_text)
