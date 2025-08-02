import os
from datetime import datetime

import pandas as pd

from src.reports import save_to_file, spending_by_category
from src.services import get_analysis_categories_of_increased_cashback, investment_bank
from src.utils import greeting, reader_excel_file
from src.views import home_page

if __name__ == "__main__":

    while True:
        try:
            operations = reader_excel_file("../data/operations.xlsx")
            user_input = input(
                f"""{greeting()} Добро пожаловать в приложение для анализа транзакций из Excel-файла!
Выберите необходимый пункт меню:
1. Веб-страница "Главная"
2. Сервисы
3. Отчет "Траты по категории"
"""
            )
            if user_input in ["1", "2", "3"]:
                if user_input == "1":
                    print('\nОтлично! Вы выбрали веб-страницу "Главная"')

                    while True:
                        user_date = input(
                            """Введите дату для анализа и вывода на веб-страницах в формате YYYY-MM-DD HH:MM:SS
"""
                        )
                        try:
                            datetime.strptime(user_date, "%Y-%m-%d %H:%M:%S")
                            break
                        except ValueError:
                            print("Дата введена неверно. Попробуйте ещё раз.")
                    print(home_page(operations, user_date))

                elif user_input == "2":
                    user_service = input(
                        """\nОтлично! Вы выбрали раздел "Сервисы"
Если Вас интересуют "Выгодные категории повышенного кешбэка", введите 1
Если Вас интересует "Инвесткопилка", введите 2
Если Вас интересуют оба варианта, введите 3
"""
                    )
                    if user_service in ["1", "2", "3"]:
                        if user_service == "1" or user_service == "3":
                            print(
                                """Вы выбрали сервис "Выгодные категории повышенного кешбэка"
Сервис позволяет проанализировать, какие категории были наиболее выгодными
для выбора в качестве категорий повышенного кешбэка.
Введите данные для анализа:"""
                            )
                            while True:
                                user_year = input("Год (например, 2018): ")
                                user_month = input("Месяц (например, 03): ")
                                if (
                                    len(user_year) == 4
                                    and len(user_month) == 2
                                    and 0 < int(user_month) <= 12
                                    and user_year.isdigit()
                                ):
                                    break
                                else:
                                    print("Данные введены некорректно")
                            result = get_analysis_categories_of_increased_cashback(operations, user_year, user_month)
                            print(result)
                        if user_service == "2" or user_service == "3":
                            print(
                                """Вы выбрали сервис "Инвесткопилка"
"Инвесткопилка" позволяет копить через округление ваших трат.
Можно задать комфортный порог округления: 10, 50 или 100 ₽.
Траты будут округляться, и разница между фактической суммой трат по карте
и суммой округления будет попадать на счет «Инвесткопилки».

Сервис показывает сумму, которую удалось бы отложить в «Инвесткопилку»"""
                            )
                            while True:
                                limit = int(
                                    input(
                                        """Выберите шаг округления в рублях 10, 50 или 100
"""
                                    )
                                )
                                if limit in [10, 50, 100]:
                                    print(f"Вы настроили шаг округления {limit} ₽")
                                    break
                                else:
                                    print("Шаг округления введен неккоректно")
                            while True:
                                month = input(
                                    """Введите год и месяц для которого
рассчитывается отложенная сумма (например, 2018-03)
"""
                                )
                                date = month.split("-")
                                if len(date[0]) == 4 and len(date[1]) == 2 and date[0].isdigit() and date[1].isdigit():
                                    break
                                else:
                                    print("Данные введены неккоректно")
                            invest_result = investment_bank(month, operations, limit)
                            print(
                                f"За {month} при округлении ваших трат до {limit} руб. "
                                f'удалось бы отложить на "Инвесткопилку": {invest_result}'
                            )
                elif user_input == "3":
                    transactions = pd.DataFrame(operations)
                    print(
                        """\nОтлично! Вы выбрали отчет "Траты по категории"
Сервис отчет "Траты по категории" выдает траты по заданной категории
за последние три месяца (от переданной или текущей даты)"""
                    )
                    while True:
                        date_for_report = input(
                            'Отчет "Траты по категории" необходим для текущей даты? да/нет\n'
                        ).lower()
                        if date_for_report == "да":
                            date_report = None
                            break
                        elif date_for_report == "нет":
                            while True:
                                date_report = input(
                                    """Введите дату для формирования отчета (например, 10.10.2020)
"""
                                )
                                try:
                                    datetime.strptime(date_report, "%d.%m.%Y").date()
                                    break
                                except ValueError:
                                    print("Дата введена неверно. Попробуйте ещё раз.")
                            break
                        else:
                            print('Внимательнее, нужно ввести "да" или "нет"')

                    category = input(
                        """Введите категорию для отчета
"""
                    ).capitalize()
                    decorated_func = save_to_file(enabled=False)(spending_by_category)

                    result = decorated_func(transactions, category, date_report)

                    if result.empty == False:
                        while True:
                            enabled_input = input("Сохранить отчет в файл? да/нет\n").lower()

                            if enabled_input == "да":

                                while True:
                                    file_input = input('Отчет сохранить в файл "report.json"? да/нет\n').lower()
                                    if file_input == "да":
                                        filename = "report.json"
                                        break
                                    elif file_input == "нет":

                                        valid_extensions = [".json", ".csv", ".xlsx"]
                                        while True:
                                            file_name = input(
                                                "Введите название файла (с расширением, например report.json): "
                                            )
                                            file_name_ext = file_name.split(".")
                                            if ("." + file_name_ext[1]) in valid_extensions:
                                                filename = file_name
                                                break
                                            else:
                                                print(
                                                    f"Неподдерживаемый формат! Допустимы: "
                                                    f"{', '.join(valid_extensions)}"
                                                )
                                        filename = file_name
                                        break

                                    else:
                                        print('Внимательнее, нужно ввести "да" или "нет"')

                                decorated_func_save = save_to_file(filename=filename, enabled=True)(
                                    spending_by_category
                                )
                                decorated_func_save(transactions, category, date_report)
                                print(
                                    f'Отчет сохранен в файл: '
                                    f'{os.path.join(os.path.dirname(os.getcwd()), "reports", filename)}'
                                )
                                break

                            elif enabled_input == "нет":
                                print(result)
                                break

                            else:
                                print('Внимательнее, нужно ввести "да" или "нет"')
                else:
                    print("Пункт введен неккоректно")
                break
            else:
                print("Пункт введен неккоректно")
        except Exception as ex:
            print(f"Произошла ошибка {ex}")


