from __future__ import annotations

import base64
import json
import mimetypes
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from openai import OpenAI
from pypdf import PdfReader

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.claim_models import InvoiceExtractionResult


INVOICE_EXTRACTION_PROMPT = """
You are an expert at reading invoices. Extract the invoice/transaction id, total amount,
and currency from the provided content. Return JSON only.

Schema:
{
  "invoice_id": "string",
  "total_amount": 0,
  "currency": "IDR",
  "confidence": 0.0
}
"""


def _normalize_invoice_id(invoice_id: str) -> str:
    invoice_id = (invoice_id or "").strip()
    if invoice_id.startswith("#"):
        invoice_id = invoice_id[1:]
    invoice_id = re.sub(r"[\s\-]+", "", invoice_id)
    return invoice_id


def _parse_amount(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    value = str(raw).strip()
    if not value:
        return None
    value = re.sub(r"[^0-9,\.]", "", value)
    if not value:
        return None

    dot_count = value.count(".")
    comma_count = value.count(",")

    if dot_count > 0 and comma_count == 0:
        if dot_count > 1:
            value = value.replace(".", "")
        else:
            left, right = value.split(".")
            if len(right) == 3 and len(left) >= 1:
                value = left + right
    if value.count(",") > 0 and value.count(".") > 0:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "")
            value = value.replace(",", ".")
        else:
            value = value.replace(",", "")
    else:
        if value.count(",") == 1 and value.count(".") == 0:
            value = value.replace(",", ".")
        elif value.count(",") > 1 and value.count(".") == 0:
            value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


class InvoiceParser:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def parse_invoice(self, file_path: Path) -> InvoiceExtractionResult:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        if mime_type == "application/pdf":
            return self._parse_pdf(file_path)
        return self._parse_image(file_path, mime_type)

    def _parse_pdf(self, file_path: Path) -> InvoiceExtractionResult:
        reader = PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages[:3]:
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text)
        text = "\n".join(text_parts).strip()
        if not text:
            raise ValueError("No text extracted from PDF. Provide an image invoice instead.")

        return self._parse_with_llm(text_content=text)

    def _parse_image(self, file_path: Path, mime_type: str) -> InvoiceExtractionResult:
        image_b64 = base64.b64encode(file_path.read_bytes()).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_b64}"
        return self._parse_with_llm(image_data_url=data_url)

    def _parse_with_llm(
        self,
        text_content: Optional[str] = None,
        image_data_url: Optional[str] = None,
    ) -> InvoiceExtractionResult:
        content = [{"type": "text", "text": INVOICE_EXTRACTION_PROMPT}]
        if text_content:
            content.append({"type": "text", "text": text_content})
        if image_data_url:
            content.append({"type": "image_url", "image_url": {"url": image_data_url}})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content or "{}"
        raw_json = self._safe_load_json(raw_text)

        invoice_id = _normalize_invoice_id(str(raw_json.get("invoice_id") or ""))
        total_amount = _parse_amount(raw_json.get("total_amount")) or 0.0
        currency = raw_json.get("currency")
        confidence = raw_json.get("confidence")
        try:
            confidence_f = float(confidence) if confidence is not None else None
        except (ValueError, TypeError):
            confidence_f = None

        return InvoiceExtractionResult(
            invoice_id=invoice_id or None,
            total_amount=total_amount,
            currency=currency,
            confidence=confidence_f,
            raw=raw_json if raw_json else {"raw_text": raw_text},
        )

    @staticmethod
    def _safe_load_json(text: str) -> Dict[str, Any]:
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            return {}
        return {}


invoice_parser = InvoiceParser()
