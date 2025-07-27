import json

from src.services import get_analysis_categories_of_increased_cashback


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
