import json
import math
from _datetime import datetime

from src.reader import reader_excel_file


def get_analysis_categories_of_increased_cashback(data, year, month):
    """Функция анализирует выгодность категории повышенного кешбэка"""
    cashback = {}
    flag = 0     #  флаг для определения нахождения операций по введенным данным
    try:
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
            return f"По введенным параметрам ({year} год, {month} месяц) кэшбэка не было"
        elif flag > 0:
            return json.dumps(cashback, ensure_ascii=False, indent=4)
        elif flag == 0:
            return f"По введенным параметрам ({year} год, {month} месяц) нет данных"
    except Exception as ex:
        return f"Произошла ошибка {ex}"


def investment_bank(month, operations, limit):
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку»"""
    if limit not in [10, 50, 100]:
        raise ValueError("Limit должен быть 10, 50 или 100")
    try:
        date = month.split('-')
        if len(date[0]) == 4 and len(date[1]) == 2:
            investment_amount = 0
            flag = 0
            for operation in operations:
                date_string = operation["Дата операции"]
                date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
                if date_operation.year == int(date[0]) and date_operation.month == int(date[1]):
                    flag += 1
                    if operation["Сумма платежа"] < 0:
                        round_amount = math.ceil(-operation["Сумма платежа"]/ limit) * limit
                        deferred_amount = round_amount + operation["Сумма платежа"]
                        investment_amount += deferred_amount
            if flag == 0:
                return f"За {month} нет данных"
            # return f"""За {month} при округлении ваших трат до {limit} руб. удалось бы отложить на "Инвесткопилку": {round(investment_amount, 2)} руб."""
            return round(investment_amount, 2)
        else:
            return f"Введенные данные: {month} - неверны"
    except Exception as ex:
        return f'Произошла ошибка {ex}'


# data = reader_excel_file("../data/operations.xlsx")
# # print(get_analysis_categories_of_increased_cashback(data, "2018", "3"))
# print(investment_bank('мама-03', data, 50))
