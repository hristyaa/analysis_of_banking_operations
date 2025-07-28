import json
import requests
import pandas as pd
from datetime import datetime
from src.reader import reader_excel_file


def home_page():
    pass


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


def get_data_of_cards(operations, start_date, end_date):
    """Функция, которая возвращает список словарей с данными по каждой карте в заданном периоде"""
    list_data_of_cards = []
    numbers_cards = []
    flag_date = 0
    flag_total = 0
    try:
        for operation in operations:
            date_string = operation["Дата операции"]
            date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
            if start_date <= date_operation <= end_date:
                flag_date += 1
                if operation["Сумма платежа"] < 0:
                    flag_total += 1
                    dict_card = {}
                    number_card = operation["Номер карты"][-4:]
                    amount = operation["Сумма платежа"]
                    cashback = int(amount / 100)
                    if number_card in numbers_cards:
                        for card in list_data_of_cards:
                            if card.get("last_digits") == number_card:
                                card["total_spent"] += -amount
                                card["cashback"] += -cashback
                    else:
                        numbers_cards.append(number_card)
                        dict_card["last_digits"] = number_card
                        dict_card["total_spent"] = -amount
                        dict_card["cashback"] = -cashback
                        list_data_of_cards.append(dict_card)

        if flag_date == 0:
            return "Данных об операциях в заданном диапазоне нет"
        if flag_total == 0:
            return "Данных в заданном диапазоне по расходам нет"
        return list_data_of_cards
    except Exception as ex:
        return f"Произошла ошибка {ex}"


def get_top_list_transction(operations, start_date, end_date):
    '''Функция формирует лист словарей "Топ-5 транзакций по сумме платежа"'''
    date = []
    amount = []
    category = []
    description = []
    flag_date = 0
    try:
        for operation in operations:
            date_string = operation["Дата операции"]
            date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
            if start_date <= date_operation <= end_date:
                flag_date += 1
                date.append(operation["Дата платежа"])
                amount.append(operation["Сумма платежа"])
                category.append(operation["Категория"])
                description.append(operation["Описание"])
        dict_transactions = {}
        dict_transactions["date"] = date
        dict_transactions["amount"] = amount
        dict_transactions["category"] = category
        dict_transactions["description"] = description
        df = pd.DataFrame.from_dict(dict_transactions)
        top_transactions = df.sort_values(by="amount", ascending=True).head()
        if flag_date == 0:
            return "Данных об операциях в заданном диапазоне нет"
        # list_transactions.append(dict_card)
        return top_transactions.to_dict(orient="records")
    except Exception as ex:
        return f"Произошла ошибка {ex}"


def get_currency_rates():
    pass


def get_stock_prices():
    pass



def home_page(operations, date):
    """
    Главная функция, возвращает json-ответ cо следующими данными:
    - Приветствие в формате "???", где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени.
    - По каждой карте:
    последние 4 цифры карты;
    общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей).
    - Топ-5 транзакций по сумме платежа.
    - Курс валют.
    - Стоимость акций из S&P500.
    """
    dict_home_page = {}
    dict_home_page["greeting"] = greeting()
    start_date, end_date = get_start_and_end_date(date)
    dict_home_page["cards"] = get_data_of_cards(operations, start_date, end_date)
    dict_home_page["top_transactions"] = get_top_list_transction(operations, start_date, end_date)

    return json.dumps(dict_home_page, ensure_ascii=False, indent=4)


data = reader_excel_file("../data/operations.xlsx")
date = "2018-03-05 12:00:00"
# print(greeting())
start_date, end_date = get_start_and_end_date("2018-03-05 12:00:00")
# print(get_data_of_cards(data, start_date, end_date))
print(get_top_list_transction(data, start_date, end_date))
# print(home_page(data, date))
