from datetime import date

from app.services.proration_service import calculate_prorated_amount, calculate_working_days_in_range


def test_calculate_working_days_in_range_excludes_weekends_and_holidays():
    start = date(2026, 1, 5)  # Monday
    end = date(2026, 1, 11)   # Sunday
    holidays = {date(2026, 1, 7)}
    assert calculate_working_days_in_range(start, end, holidays) == 4


def test_calculate_prorated_amount():
    assert calculate_prorated_amount(1000, 10, 20) == 500
