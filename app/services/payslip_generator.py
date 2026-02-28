from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import PAYSLIP_TEMPLATE, PAYSLIP_OUTPUT_DIR
from app.models.payslip_models import PayslipData


def _format_currency(amount: float) -> str:
    return f"Rp {amount:,.0f}"


def render_payslip_html(payslip_data: PayslipData, template_path: Path = PAYSLIP_TEMPLATE) -> str:
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["currency"] = _format_currency
    template = env.get_template(template_path.name)
    return template.render(payslip=payslip_data.model_dump())


def generate_payslip_pdf(
    payslip_data: PayslipData,
    output_dir: Path = PAYSLIP_OUTPUT_DIR,
    template_path: Path = PAYSLIP_TEMPLATE,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{payslip_data.employee_id}-{payslip_data.period}.pdf"
    output_path = output_dir / filename
    html_content = render_payslip_html(payslip_data, template_path)

    from weasyprint import HTML

    HTML(string=html_content, base_url=str(template_path.parent)).write_pdf(str(output_path))
    return output_path


def build_payslip_context(metadata: Dict[str, Any]) -> PayslipData:
    metadata = dict(metadata)
    metadata.setdefault("generated_at", datetime.utcnow())
    return PayslipData.model_validate(metadata)
