import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.reader import reader_excel_file

load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")


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
    """Функция возвращает курс валют"""
    try:
        if not API_KEY:
            raise ValueError("API_KEY не задан!")

        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB"
        response = requests.get(url)

        if response.status_code != 200:
            raise ValueError(f"Ошибка запроса: {response.status_code}")

        data = response.json()

        if data.get("conversion_rates") is None:
            raise KeyError("Ключ 'conversion_rates' отсутствует в ответе API")

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user_settings.json"))
        with open(file_path, "r", encoding="utf-8") as file:
            user_settings = json.load(file)
            user_currencies = user_settings["user_currencies"]

        currency_list = []
        for currency in user_currencies:
            try:
                rate = data["conversion_rates"][currency]
                dict_currency = {}
                dict_currency["currency"] = currency
                dict_currency["rate"] = round(1 / rate, 2)
                currency_list.append(dict_currency)
            except KeyError:
                continue

        return currency_list

    except ValueError as ve:
        raise ve

    except Exception as ex:
        return f"Произошла ошибка {ex}"


def get_stock_prices():
    """Функция стоимость акций из S&P500"""

    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user_settings.json"))
    with open(file_path, "r", encoding="utf-8") as file:
        user_settings = json.load(file)
        user_stocks = user_settings["user_stocks"]

    stocks_list = []

    for stock in user_stocks:
        try:
            url = f"https://api.twelvedata.com/price?symbol={stock}&apikey={SECRET_API_KEY}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Ошибка запроса для {stock}: {response.status_code}")
                continue

            data = response.json()
            print(data)
            dict_stock = {}
            if data.get("price"):
                dict_stock["stock"] = stock
                dict_stock["price"] = round(float(data.get("price")), 2)
                stocks_list.append(dict_stock)
            else:
                print(f"{stock}: не удалось получить цену")
                continue

        except Exception as ex:
            print(f"Произошла ошибка {ex} при получении данных {stock}")

    return stocks_list


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
    dict_home_page["currency_rates"] = get_currency_rates()
    dict_home_page["stock_prices"] = get_stock_prices()

    return json.dumps(dict_home_page, ensure_ascii=False, indent=4)


# data = reader_excel_file("../data/operations.xlsx")
# date = "2018-03-05 12:00:00"
# # # # # print(greeting())
# # # # start_date, end_date = get_start_and_end_date("2018-03-05 12:00:00")
# # # # # print(get_data_of_cards(data, start_date, end_date))
# # # # # print(get_top_list_transction(data, start_date, end_date))
# print(home_page(data, date))
# # print(get_currency_rates())
print(get_stock_prices())
