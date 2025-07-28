import pytest
from datetime import datetime
from unittest.mock import patch
from src.views import greeting, get_start_and_end_date, get_data_of_cards, get_top_list_transction


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
