import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import get_start_and_end_date, greeting, reader_excel_file

views_logger = logging.getLogger("app.views")

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(filename=os.path.join(log_dir, "views.log"), mode="w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)


load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")


def get_data_of_cards(operations, start_date, end_date):
    """Функция, которая возвращает список словарей с данными по каждой карте в заданном периоде"""
    list_data_of_cards = []
    numbers_cards = []
    flag_date = 0
    flag_total = 0
    try:
        views_logger.info("Попытка нахождения операций по введенным параметрам")
        for operation in operations:
            date_string = operation.get("Дата операции")

            date_operation = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
            if start_date <= date_operation <= end_date:
                flag_date += 1
                if operation.get("Сумма платежа") < 0:
                    flag_total += 1
                    dict_card = {}
                    if not operation.get("Номер карты") or str(operation.get("Номер карты")).lower() == "nan":
                        views_logger.warning(f"Пропущена операция без корректного номера карты: {operation}")
                        continue
                    else:
                        number_card = operation.get("Номер карты")[-4:]

                        amount = operation.get("Сумма платежа")
                        cashback = float(amount / 100)
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
            views_logger.warning("Данных об операциях в заданном диапазоне нет")
            return "Данных об операциях в заданном диапазоне нет"
        if flag_total == 0:
            views_logger.warning("Данных в заданном диапазоне по расходам нет")
            return "Данных в заданном диапазоне по расходам нет"
        views_logger.info("Получен список словарей с данными по каждой карте в заданном периоде")
        for card in list_data_of_cards:
            card["total_spent"] = round(card["total_spent"], 2)
            card["cashback"] = round(card["cashback"], 2)
        return list_data_of_cards
    except Exception as ex:
        views_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


def get_top_list_transction(operations, start_date, end_date):
    '''Функция формирует лист словарей "Топ-5 транзакций по сумме платежа"'''
    date = []
    amount = []
    category = []
    description = []
    flag_date = 0
    try:
        views_logger.info("Попытка нахождения операций по введенным параметрам")
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
            views_logger.warning("Данных об операциях в заданном диапазоне нет")
            return "Данных об операциях в заданном диапазоне нет"
        # list_transactions.append(dict_card)
        views_logger.info("Лист словарей 'Топ-5 транзакций по сумме платежа' сформирован")
        return top_transactions.to_dict(orient="records")
    except Exception as ex:
        views_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


def get_currency_rates():
    """Функция возвращает курс валют"""
    try:
        if not API_KEY:
            views_logger.error("API_KEY не задан!")
            raise ValueError("API_KEY не задан!")

        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB"
        response = requests.get(url)

        views_logger.info(f"Отправляем GET запрос к URL: {url}")

        if response.status_code != 200:
            views_logger.error(f"Ошибка запроса: {response.status_code}")
            raise ValueError(f"Ошибка запроса: {response.status_code}")

        data = response.json()

        if data.get("conversion_rates") is None:
            views_logger.error("Ключ 'conversion_rates' отсутствует в ответе API")
            raise KeyError("Ключ 'conversion_rates' отсутствует в ответе API")

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user_settings.json"))

        with open(file_path, "r", encoding="utf-8") as file:
            views_logger.info("Открытие файла пользовательских настроек user_settings.json")
            user_settings = json.load(file)
            user_currencies = user_settings["user_currencies"]

        currency_list = []
        views_logger.info("Формирование листа курса валют")
        for currency in user_currencies:
            try:
                rate = data["conversion_rates"][currency]
                dict_currency = {}
                dict_currency["currency"] = currency
                dict_currency["rate"] = round(1 / rate, 2)
                currency_list.append(dict_currency)
            except KeyError:
                views_logger.error(f"Ошибка при получении курса для валюты: {currency}")
                continue
        views_logger.info("Лист курса валют сформирован")
        return currency_list

    except ValueError as ve:
        views_logger.error("Произошла ошибка ValueError")
        raise ve

    except Exception as ex:
        views_logger.error("Произошла ошибка")
        return f"Произошла ошибка {ex}"


def get_stock_prices():
    """Функция стоимость акций из S&P500"""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user_settings.json"))

    views_logger.info("Открытие файла пользовательских настроек user_settings.json")

    with open(file_path, "r", encoding="utf-8") as file:
        user_settings = json.load(file)
        user_stocks = user_settings["user_stocks"]

    stocks_list = []

    for stock in user_stocks:
        try:
            url = f"https://api.twelvedata.com/price?symbol={stock}&apikey={SECRET_API_KEY}"
            response = requests.get(url)

            views_logger.info(f"Отправляем GET запрос к URL: {url} для {stock}")

            if response.status_code != 200:
                views_logger.error(f"Ошибка запроса для {stock}: {response.status_code} ")
                print(f"Ошибка запроса для {stock}: {response.status_code}")
                continue

            data = response.json()

            dict_stock = {}
            if data.get("price"):
                dict_stock["stock"] = stock
                dict_stock["price"] = round(float(data.get("price")), 2)
                views_logger.info(f"Стоимость для {stock} получена")
                stocks_list.append(dict_stock)
            else:
                views_logger.warning(f"Стоимость для {stock} не удалось получить")
                print(f"{stock}: не удалось получить цену")
                continue

        except Exception as ex:
            views_logger.error(f"Произошла ошибка при получении данных {stock}")
            print(f"Произошла ошибка {ex} при получении данных {stock}")
    views_logger.info("Вывод полученных стоимостей акций из S&P500")
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
    views_logger.info("Cтраница 'Главная' успешно реализована")
    return json.dumps(dict_home_page, ensure_ascii=False, indent=4)

#
# data = reader_excel_file("../data/operations.xlsx")
# date = "2018-03-15 12:00:00"
# # # # print(greeting())
# start_date, end_date = get_start_and_end_date("2018-03-15 12:00:00")
# print(get_data_of_cards(data, start_date, end_date))
# # # print(get_top_list_transction(data, start_date, end_date))
# print(home_page(data, date))
# print(get_currency_rates())
# print(get_stock_prices())
