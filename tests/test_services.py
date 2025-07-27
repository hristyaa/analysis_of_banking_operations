import json
import pytest
from src.services import get_analysis_categories_of_increased_cashback, investment_bank


def test_get_analysis_categories_of_increased_cashback(operations):
    """Тестирование на правильный анализ категории кэшбека при верно заданных параметрах"""
    result = get_analysis_categories_of_increased_cashback(operations, "2018", "3")
    assert result == json.dumps({"Транспорт": 2, "Ж/д билеты": 15}, ensure_ascii=False, indent=4)


def test_get_analysis_categories_no_data(operations):
    """Тестирование на анализ категории кэшбека при отсутствиии данных"""
    result = get_analysis_categories_of_increased_cashback(operations, "2019", "3")
    assert result == "По введенным параметрам (2019 год, 3 месяц) нет данных"


def test_get_analysis_categories_no_cashback(operations):
    """Тестирование на анализ категории кэшбека при отсутствиии кэшбэка"""
    result = get_analysis_categories_of_increased_cashback(operations, "2018", "2")
    assert result == "По введенным параметрам (2018 год, 2 месяц) кэшбэка не было"


def test_get_analysis_categories_incorrect_params(operations):
    """Тестирование на анализ категории кэшбека при неверно заданных параметрах"""
    result = get_analysis_categories_of_increased_cashback(operations, "2hg018424", "2")
    assert result == "Произошла ошибка invalid literal for int() with base 10: '2hg018424'"


@pytest.mark.parametrize("month, limit, expected", [("2018-03", 10, 16.9),
                                                    ("2018-03", 50, 106.9),
                                                    ("2018-03", 100, 206.9)])
def test_investment_bank(month, operations, limit, expected):
    """Тест функции при верно заданных параметрах"""
    result = investment_bank(month, operations, limit)
    assert result == expected


def test_investment_bank_invalid_limit(operations):
    """Тест функции при неверно заданном лимите"""
    with pytest.raises(ValueError):
        investment_bank("2018-03", operations, 110)


def test_investment_bank_no_date(operations):
    """Тест функции при отсутствии данных в заданном месяце"""
    result = investment_bank("2025-03", operations, 10)
    assert result == "За 2025-03 нет данных"


def test_investment_bank_invalid_date(operations):
    """Тест функции при неверно заданном месяце"""
    result = investment_bank("20425-03", operations, 10)
    assert result == "Введенные данные: 20425-03 - неверны"
    result = investment_bank("nj41-03", operations, 10)
    assert result == "Произошла ошибка invalid literal for int() with base 10: 'nj41'"
