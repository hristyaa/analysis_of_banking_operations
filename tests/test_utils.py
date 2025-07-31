from datetime import datetime
from unittest.mock import patch

import pytest

from src.utils import get_start_and_end_date, greeting, reader_excel_file


@patch("src.utils.pd.read_excel")
def test_reader_excel_file(mock_read_excel):
    """Тест при excel файле c данными"""
    mock_read_excel.return_value.to_dict.return_value = """[
        {
        "Дата операции": "01.01.2018 20:27:51",
        "Дата платежа": "04.01.2018",
        "Номер карты": "*7197",
        "Статус": "OK",
        "Сумма операции": -316.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -316.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": NaN,
        "Категория": "Красота",
        "MCC": 5977.0,
        "Описание": "OOO Balid",
        "Бонусы (включая кэшбэк)": 6,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 316.0
    },
    {
        "Дата операции": "01.01.2018 12:49:53",
        "Дата платежа": "01.01.2018",
        "Номер карты": NaN,
        "Статус": "OK",
        "Сумма операции": -3000.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -3000.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": NaN,
        "Категория": "Переводы",
        "MCC": NaN,
        "Описание": "Линзомат ТЦ Юность",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 3000.0
    }
]"""

    expected_result = """[
        {
        "Дата операции": "01.01.2018 20:27:51",
        "Дата платежа": "04.01.2018",
        "Номер карты": "*7197",
        "Статус": "OK",
        "Сумма операции": -316.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -316.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": NaN,
        "Категория": "Красота",
        "MCC": 5977.0,
        "Описание": "OOO Balid",
        "Бонусы (включая кэшбэк)": 6,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 316.0
    },
    {
        "Дата операции": "01.01.2018 12:49:53",
        "Дата платежа": "01.01.2018",
        "Номер карты": NaN,
        "Статус": "OK",
        "Сумма операции": -3000.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -3000.0,
        "Валюта платежа": "RUB",
        "Кэшбэк": NaN,
        "Категория": "Переводы",
        "MCC": NaN,
        "Описание": "Линзомат ТЦ Юность",
        "Бонусы (включая кэшбэк)": 0,
        "Округление на инвесткопилку": 0,
        "Сумма операции с округлением": 3000.0
    }
]"""
    assert reader_excel_file("mock_file.xlsx").replace(" ", "").replace("\n", "") == expected_result.strip().replace(
        " ", ""
    ).replace("\n", "")


def test_reader_excel_empty_file(excel_empty_file):
    """Тест при пустом excel файле"""
    result = reader_excel_file(excel_empty_file)
    assert result == "Файл пустой."


def test_reader_excel_file_file_not_found():
    """Тест, если файл не найден"""
    result = reader_excel_file("file_non_existent.xlsx")
    assert result == "Файл не найден."


def test_reader_excel_file_file_invalid_file_format(txt_file):
    """Тест, если файл с неправильным форматом"""
    result = reader_excel_file(txt_file)
    assert result == "Файл пустой или имеет неподдерживаемый формат."


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
    with patch("src.utils.datetime") as mock_datetime:
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
