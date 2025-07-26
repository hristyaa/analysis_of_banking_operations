import json

from _datetime import datetime

from src.reader import reader_excel_file


def get_analysis_categories_of_increased_cashback(data, year, month):
    """ Функция анализирует выгодность категории повышенного кешбэка"""
    # date_obj = datetime(int(year), int(month), 1)
    # date_analysis = date_obj.strftime('%d.%m.%Y')
    # date_obj_to = datetime(int(year), int(month), 31)
    # date_analysis_to = date_obj_from.strftime('%d.%m.%Y')
    cashback = {}
    for operation in data:
        date_string = operation['Дата операции']
        date_operation = datetime.strptime(date_string, '%d.%m.%Y %H:%M:%S')
        # print(type(date_operation.year))
        # print(type(date_operation.month))
        if date_operation.year == int(year) and date_operation.month == int(month):
            # print(operation)
            if operation['Кэшбэк'] > 0:
                cash = operation['Кэшбэк']
                category = operation['Категория']
                if cashback.get(category) is None:
                    cashback[category] = int(cash)
                else:
                    new_cash = cashback.get(category) + cash
                    cashback[category] = int(new_cash)
    return json.dumps(cashback, ensure_ascii=False, indent=4)

    # print(date_analysis)


data = reader_excel_file('../data/operations.xlsx')
print(get_analysis_categories_of_increased_cashback(data, '2018', '3'))
