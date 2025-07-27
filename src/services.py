import json

from _datetime import datetime

from src.reader import reader_excel_file


def get_analysis_categories_of_increased_cashback(data, year, month):
    """Функция анализирует выгодность категории повышенного кешбэка"""
    cashback = {}
    flag = 0
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

    # print(date_analysis)


data = reader_excel_file("../data/operations.xlsx")
print(get_analysis_categories_of_increased_cashback(data, "2018", "3"))
