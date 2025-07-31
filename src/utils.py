import pandas as pd
from datetime import datetime


def reader_excel_file(file_excel_path):
    """Функция считывает данные из Excel и выдает список словарей с банковскими операциями."""
    try:
        operations_excel = pd.read_excel(file_excel_path)
        return operations_excel.to_dict(orient="records")

    except FileNotFoundError:
        return "Файл не найден."
    except (pd.errors.EmptyDataError, ValueError) as ve:
        if "Excel file format cannot be determined" in str(ve):
            return "Файл пустой или имеет неподдерживаемый формат."
        return "Файл пустой."
    except Exception as ex:
        return f"Произошла ошибка: {ex}."


def greeting():
    """Функция приветствия в зависимости от текущего времени"""
    current_date_time = datetime.now()
    if 6 <= current_date_time.hour <= 11:
        return "Доброе утро!"
    elif 12 <= current_date_time.hour <= 17:
        return "Добрый день!"
    elif 18 <= current_date_time.hour <= 23:
        return "Добрый вечер!"
    elif 0 <= current_date_time.hour < 5:
        return "Доброй ночи!"


def get_start_and_end_date(date):
    """Функция, которая определяет диапазон дат для анализа"""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
        end_date = date_obj
        return start_date, end_date
    except Exception as ex:
        return f"Произошла ошибка {ex}"


# print(reader_excel_file("../data/operations.xlsx"))