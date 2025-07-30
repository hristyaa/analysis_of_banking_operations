from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.views import (get_currency_rates, get_data_of_cards, get_start_and_end_date, get_stock_prices,
                       get_top_list_transction, greeting)


@pytest.mark.parametrize(
    "test_time, expected",
    [
        ("2025-03-05 08:10:15", "Доброе утро!"),
        ("2025-03-05 14:10:15", "Добрый день!"),
        ("2025-03-05 18:10:15", "Добрый вечер!"),
        ("2025-03-05 02:10:15", "Доброй ночи!"),
    ],
)
def test_greeting(test_time, expected):
    """Тест на правильное приветствие"""
    mock_time = datetime.strptime(test_time, "%Y-%m-%d %H:%M:%S")
    with patch("src.views.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_time
        assert greeting() == expected


def test_get_start_and_end_date():
    """Проверка функцию на правильную выдачу диапазона"""
    result = get_start_and_end_date("2018-03-05 08:10:15")
    assert result == (datetime(2018, 3, 1, 0, 0, 0), datetime(2018, 3, 5, 8, 10, 15))


def test_get_start_and_end_date_error():
    """Тест на обработку функции при неправильном формате даты"""
    result = get_start_and_end_date("03-05-2018 08:10:15")
    assert result == "Произошла ошибка time data '03-05-2018 08:10:15' does not match format '%Y-%m-%d %H:%M:%S'"


@pytest.mark.parametrize(
    "start_date, end_date, excepted",
    [
        (
            datetime(2018, 3, 1, 0, 0, 0),
            datetime(2018, 3, 22, 15, 0, 0),
            [
                {"last_digits": "7197", "total_spent": 310, "cashback": 3},
                {"last_digits": "4556", "total_spent": 300, "cashback": 3},
            ],
        ),
        (
            datetime(2018, 3, 1, 0, 0, 0),
            datetime(2018, 3, 5, 15, 0, 0),
            "Данных об операциях в заданном диапазоне нет",
        ),
        (
            datetime(2018, 2, 1, 0, 0, 0),
            datetime(2018, 2, 27, 12, 36, 0),
            "Данных в заданном диапазоне по расходам нет",
        ),
        (
            "2018, 12, 1, 0, 0, 0",
            "2018, 12, 1, 0, 0, 0",
            "Произошла ошибка '<=' not supported between instances of 'str' and 'datetime.datetime'",
        ),
    ],
)
def test_get_data_of_cards(operations, start_date, end_date, excepted):
    """Тест на обработку функции при заданных параметрах"""
    assert get_data_of_cards(operations, start_date, end_date) == excepted


@pytest.mark.parametrize(
    "start_date, end_date, excepted",
    [
        (
            datetime(2018, 3, 1, 0, 0, 0),
            datetime(2018, 3, 22, 15, 0, 0),
            [
                {"date": "24.03.2018", "amount": -310.0, "category": "Фастфуд", "description": "OOO Frittella"},
                {
                    "date": "13.03.2018",
                    "amount": -300.0,
                    "category": "Ж/д билеты",
                    "description": "Московский метрополитен",
                },
            ],
        ),
        (
            datetime(2018, 3, 1, 0, 0, 0),
            datetime(2018, 3, 5, 15, 0, 0),
            "Данных об операциях в заданном диапазоне нет",
        ),
        (
            "2018, 12, 1, 0, 0, 0",
            "2018, 12, 1, 0, 0, 0",
            "Произошла ошибка '<=' not supported between instances of 'str' and 'datetime.datetime'",
        ),
    ],
)
def test_get_top_list_transction(operations, start_date, end_date, excepted):
    """Тест на обработку функции при заданных параметрах"""
    assert get_top_list_transction(operations, start_date, end_date) == excepted


def test_get_currency_rates():
    """Тест на работу функции"""
    test_data = {"conversion_rates": {"USD": 0.0124, "EUR": 0.0107}}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data

    with patch("requests.get", return_value=mock_response):
        result = get_currency_rates()

        assert result[0]["currency"] == "USD"
        assert result[0]["rate"] == round(1 / 0.0124, 2)
        assert result[1]["currency"] == "EUR"
        assert result[1]["rate"] == round(1 / 0.0107, 2)


def test_get_currency_rates_api_error():
    """Тест обработки ошибки API"""
    mock_response = Mock()
    mock_response.status_code = 500
    with pytest.raises(ValueError):
        with patch("requests.get", return_value=mock_response):
            get_currency_rates()


def test_get_stock_prices():
    """Тест на работу функции"""
    test_data = {'price': '211.27000'}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data

    with patch("requests.get", return_value=mock_response):
        result = get_stock_prices()

        assert result[0]["stock"] == "AAPL"
        assert result[0]['price'] == 211.27


def test_get_stock_prices_api_error():
    """Тест обработки ошибки API"""
    mock_response = Mock()
    mock_response.status_code = 500

    with patch("requests.get", return_value=mock_response):
        result = get_stock_prices()
        assert result == []


def test_get_stock_prices_no_key():
    """Тест на отсутствие price"""
    test_data = {'pricecc': '211.27000'}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data

    with patch("requests.get", return_value=mock_response):
        result = get_stock_prices()
        assert result == []
