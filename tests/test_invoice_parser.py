from app.services.invoice_parser import _normalize_invoice_id, _parse_amount


def test_normalize_invoice_id_strips_hash_and_spaces():
    assert _normalize_invoice_id(" # INV 123 ") == "INV123"


def test_parse_amount_handles_common_formats():
    assert _parse_amount("Rp 50.000") == 50000.0
    assert _parse_amount("50,000") == 50.0
    assert _parse_amount("1.234,56") == 1234.56
    assert _parse_amount("1,234.56") == 1234.56
