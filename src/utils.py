import logging
import os
from datetime import datetime

import pandas as pd

utils_logger = logging.getLogger("app.utils")

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(filename=os.path.join(log_dir, "utils.log"), mode="w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def reader_excel_file(file_excel_path):
    """Функция считывает данные из Excel и выдает список словарей с банковскими операциями."""
    try:
        utils_logger.info("Попытка считывания данных из файла")
        operations_excel = pd.read_excel(file_excel_path)
        utils_logger.info("Преобразование данных из excel-файла в словарь")
        return operations_excel.to_dict(orient="records")

    except FileNotFoundError:
        utils_logger.error("Файл не найден")
        return "Файл не найден."
    except (pd.errors.EmptyDataError, ValueError) as ve:
        utils_logger.error("Файл пустой или имеет неподдерживаемый формат")
        if "Excel file format cannot be determined" in str(ve):
            return "Файл пустой или имеет неподдерживаемый формат."
        return "Файл пустой."
    except Exception as ex:
        utils_logger.error("Произошла ошибка")
        return f"Произошла ошибка: {ex}."


def greeting():
    """Функция приветствия в зависимости от текущего времени"""
    utils_logger.info("Получение текущего времени")
    current_date_time = datetime.now()
    if 6 <= current_date_time.hour <= 11:
        utils_logger.info("Вывод приветствия в зависимости от текущего времени")
        return "Доброе утро!"
    elif 12 <= current_date_time.hour <= 17:
        utils_logger.info("Вывод приветствия в зависимости от текущего времени")
        return "Добрый день!"
    elif 18 <= current_date_time.hour <= 23:
        utils_logger.info("Вывод приветствия в зависимости от текущего времени")
        return "Добрый вечер!"
    elif 0 <= current_date_time.hour < 5:
        utils_logger.info("Вывод приветствия в зависимости от текущего времени")
        return "Доброй ночи!"


def get_start_and_end_date(date):
    """Функция, которая определяет диапазон дат для анализа"""
    try:
        utils_logger.info("Преобразование введенной даты в объект")
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        utils_logger.info("Определение даты начала диапозона с обнулением времени")
        start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
        end_date = date_obj
        return start_date, end_date
    except Exception as ex:
        utils_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


# print(reader_excel_file("../data/operations.xlsx"))
# print(greeting())
# print(get_start_and_end_date('2008-01-01 14:21:23'))
