import pytest
import pandas as pd
import os

from src.reports import save_to_file, spending_by_category

def test_decorator_save_to_file(dataframe, tmp_path):
    '''Проверка декоратора на сохранение результата функции в файл'''
    test_file = tmp_path / 'test_report.json'


    @save_to_file(filename=str(test_file))
    def test_func(df):
        return df


    # Вызываем декорированную функцию
    test_func(dataframe)

    # Проверяем эффекты декоратора
    with open(test_file, 'r', encoding='utf-8') as f:
        saved_content = f.read()

    assert test_file.exists()
    assert '"Yes": "test"' in saved_content
    assert '"No": "131"' in saved_content


def test_decorator_save_to_file_empty(dataframe_empty):
    '''Проверка декоратора при пустом датафрейме'''
    @save_to_file()
    def test_func(df):
        return df

    # Вызываем декорированную функцию
    result = test_func(dataframe_empty)

    assert result =='Запись в файл не произведена, так как нет данных'


def test_spending_by_category(dataframe_operations):
    result = spending_by_category(dataframe_operations, 'Elis')
    assert 'нет данных' in result or 'Произошла ошибка' in result


