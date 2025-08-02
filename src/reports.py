import json
import logging
import os
from datetime import datetime
from functools import wraps

import pandas as pd
from dateutil.relativedelta import relativedelta

reports_logger = logging.getLogger("app.views")

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(filename=os.path.join(log_dir, "reports.log"), mode="w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.DEBUG)


def save_to_file(filename="report.json", enabled=False):
    """
    Декоратор записывает данные отчета в файл с названием по умолчанию 'report.json' или
    в заданный файл в директорию reports
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if not enabled:
                return result

            if type(result) is str:
                return result

            if result.empty:
                reports_logger.warning("Запись в файл не произведена, так как нет данных")
                return "Запись в файл не произведена, так как нет данных"

            os.makedirs("../reports", exist_ok=True)
            filepath = os.path.join("../reports", filename)
            try:
                if filename.endswith(".csv"):
                    result.to_csv(filepath, index=False, encoding="utf-8")
                elif filename.endswith(".json"):
                    with open(filepath, "w", encoding="utf-8") as f:
                        json_str = result.to_json(orient="records", indent=4)
                        parsed = json.loads(json_str)
                        json.dump(parsed, f, ensure_ascii=False, indent=4)
                elif filename.endswith(".xlsx"):
                    result.to_excel(filepath, index=False)

                reports_logger.info(f"Отчет успешно сохранен в файл: {filepath}")

            except Exception as ex:
                reports_logger.error(f"Ошибка при сохранении файла {filename}: {ex}")
                return f"Произошла ошибка {ex}"

            return result

        return wrapper

    return decorator


@save_to_file(enabled=False)
def spending_by_category(transactions, category, date=None):
    """
    Функция возвращает траты по заданной категории
    за последние три месяца (от переданной даты) или от текущей даты (если не передана дата)
    """
    try:
        if date is None:
            date_end = datetime.now().date()
        else:
            date_end = datetime.strptime(date, "%d.%m.%Y").date()

        date_start = date_end - relativedelta(months=3)

        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y").dt.date

        date_mask = (transactions["Дата платежа"] >= date_start) & (transactions["Дата платежа"] <= date_end)
        category_mask = transactions["Категория"] == category
        df = transactions.loc[date_mask]
        df_category = df.loc[category_mask]

        if df_category.empty:
            reports_logger.warning(f"В период с {date_start} по {date_end} в категории '{category}' нет данных")
            print(f"В период с {date_start} по {date_end} в категории '{category}' нет данных")

        return df_category

    except Exception as ex:
        reports_logger.error(f"Ошибка в spending_by_category: {ex}")
        return f"Произошла ошибка {ex}"


# transactions = pd.DataFrame(reader_excel_file("../data/operations.xlsx"))
# # print(spending_by_category(transactions, 'Супермаркеты', date='21.05.2018'))
# print(spending_by_category(transactions, 'Супермаркеты', date=None))
