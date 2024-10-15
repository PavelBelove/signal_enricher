# tests/test_date_utils.py

import pytest
from datetime import datetime, timedelta
from modules.date_utils import translate_month, parse_date

def test_translate_month():
    assert translate_month("1 янв 2023") == "1 Jan 2023"
    assert translate_month("1 февр 2023") == "1 Feb 2023"
    assert translate_month("1 марта 2023") == "1 Mar 2023"
    assert translate_month("1 апр 2023") == "1 Apr 2023"
    assert translate_month("1 мая 2023") == "1 May 2023"
    assert translate_month("1 июн 2023") == "1 Jun 2023"
    assert translate_month("1 июл 2023") == "1 Jul 2023"
    assert translate_month("1 авг 2023") == "1 Aug 2023"
    assert translate_month("1 сент 2023") == "1 Sep 2023"
    assert translate_month("1 окт 2023") == "1 Oct 2023"
    assert translate_month("1 нояб 2023") == "1 Nov 2023"
    assert translate_month("1 дек 2023") == "1 Dec 2023"

def test_parse_date():
    assert parse_date("1 янв 2023") == datetime(2023, 1, 1)
    assert parse_date("1 февр 2023") == datetime(2023, 2, 1)
    assert parse_date("1 марта 2023") == datetime(2023, 3, 1)
    assert parse_date("1 апр 2023") == datetime(2023, 4, 1)
    assert parse_date("1 мая 2023") == datetime(2023, 5, 1)
    assert parse_date("1 июн 2023") == datetime(2023, 6, 1)
    assert parse_date("1 июл 2023") == datetime(2023, 7, 1)
    assert parse_date("1 авг 2023") == datetime(2023, 8, 1)
    assert parse_date("1 сент 2023") == datetime(2023, 9, 1)
    assert parse_date("1 окт 2023") == datetime(2023, 10, 1)
    assert parse_date("1 нояб 2023") == datetime(2023, 11, 1)
    assert parse_date("1 дек 2023") == datetime(2023, 12, 1)

    assert parse_date("2 дня назад").replace(microsecond=0) == (datetime.now() - timedelta(days=2)).replace(microsecond=0)
    assert parse_date("3 часа назад").replace(microsecond=0) == (datetime.now() - timedelta(hours=3)).replace(microsecond=0)
    assert parse_date("15 минут назад").replace(microsecond=0) == (datetime.now() - timedelta(minutes=15)).replace(microsecond=0)
    assert parse_date("5 дней назад").replace(microsecond=0) == (datetime.now() - timedelta(days=5)).replace(microsecond=0)
    assert parse_date("10 часов назад").replace(microsecond=0) == (datetime.now() - timedelta(hours=10)).replace(microsecond=0)
    assert parse_date("30 минут назад").replace(microsecond=0) == (datetime.now() - timedelta(minutes=30)).replace(microsecond=0)