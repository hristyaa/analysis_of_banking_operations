import json
import logging
import math
import os

from _datetime import datetime

# from src.utils import reader_excel_file

services_logger = logging.getLogger("app.services")

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(filename=os.path.join(log_dir, "services.log"), mode="w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def get_analysis_categories_of_increased_cashback(data, year, month):
    """Функция анализирует выгодность категории повышенного кешбэка"""
    cashback = {}
    flag = 0  # флаг для определения нахождения операций по введенным данным
    try:
        services_logger.info("Попытка нахождения операций по введенным параметрам")
        for operation in data:
            date_string = operation["Дата операции"]
            date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
            if date_operation.year == int(year) and date_operation.month == int(month):
                flag += 1
                if operation["Кэшбэк"] > 0:
                    cash = operation["Кэшбэк"]
                    category = operation["Категория"]
                    if cashback.get(category) is None:
                        cashback[category] = int(cash)
                    else:
                        new_cash = cashback.get(category) + cash
                        cashback[category] = int(new_cash)
        if flag > 0 and cashback == {}:
            services_logger.warning("По введенным параметрам кэшбек не найден")
            return f"По введенным параметрам ({year} год, {month} месяц) кэшбэк не найден"
        elif flag > 0:
            services_logger.info("Данные по введенным параметрам найдены, выведены в консоль в формате json")
            return json.dumps(cashback, ensure_ascii=False, indent=4)
        elif flag == 0:
            services_logger.warning("По введенным параметрам данных нет")
            return f"По введенным параметрам ({year} год, {month} месяц) нет данных"
    except Exception as ex:
        services_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


def investment_bank(month, operations, limit):
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку»"""
    if limit not in [10, 50, 100]:
        services_logger.error("Limit неверный")
        raise ValueError("Limit должен быть 10, 50 или 100")
    try:
        date = month.split("-")

        if len(date[0]) == 4 and len(date[1]) == 2:
            services_logger.info("Попытка расчета суммы, которую удалось бы отложить в «Инвесткопилку»")
            investment_amount = 0
            flag = 0
            for operation in operations:
                date_string = operation["Дата операции"]
                date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
                if date_operation.year == int(date[0]) and date_operation.month == int(date[1]):
                    flag += 1
                    if operation["Сумма платежа"] < 0:
                        round_amount = math.ceil(-operation["Сумма платежа"] / limit) * limit
                        deferred_amount = round_amount + operation["Сумма платежа"]
                        investment_amount += deferred_amount
            if flag == 0:
                services_logger.warning("За введенный месяц данных нет")
                return f"За {month} нет данных"
            # return f"""За {month} при округлении ваших трат до {limit} руб. удалось бы отложить на "Инвесткопилку":
            # {round(investment_amount, 2)} руб."""
            services_logger.info("Сумма успешно рассчитана»")
            return round(investment_amount, 2)
        else:
            services_logger.warning("Введенные данные месяца неверны")
            return f"Введенные данные: {month} - неверны"
    except Exception as ex:
        services_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


# data = reader_excel_file("../data/operations.xlsx")
# print(get_analysis_categories_of_increased_cashback(data, "2018", "3"))
# print(investment_bank('мама-03', data, 50))
