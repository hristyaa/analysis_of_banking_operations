import pandas as pd

def reader_excel_file(file_excel_path):
    """Функция считывает данные из Excel и выдает список словарей с банковскими операциями."""
    try:
        operations_excel = pd.read_excel(file_excel_path)
        return operations_excel.to_dict(orient="records")

    except FileNotFoundError:
        return "Файл не найден."
    except pd.errors.EmptyDataError:
        return "Файл пустой."
    except ValueError as ve:
        if "Excel file format cannot be determined" in str(ve):
            return "Файл пустой."
        return f"Произошла ошибка: {ve}."
    except Exception as ex:
        return f"Произошла ошибка: {ex}."


print(reader_excel_file('../data/operations.xlsx'))
