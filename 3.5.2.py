import pandas as pd
from math import isnan
import sqlite3


def get_avg_salary(row):
    """Возвращает значение для поля salary в зависимости от заполненности полей salary_from, salary_to
    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary'
    """
    avg_values = []

    avg_values += [row["salary_from"]] if not isnan(row["salary_from"]) else []
    avg_values += [row["salary_to"]] if not isnan(row["salary_to"]) else []
    if len(avg_values) != 0:
        return sum(avg_values) / len(avg_values)
    return


def converter_salaries_in_rubles(row):
    """Конвертирует salary в рубли после сравнения даты появления вакансии
    с датой в файле currencies.db
    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary' в рублях
    """
    result = []
    exchange = sqlite3.connect("currencies.db")
    cur = exchange.cursor()
    cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('currency');")
    for i in cur.fetchall():
        result.append(i[0])
    if row["salary_currency"] in result:
        cur.execute(f"SELECT {row['salary_currency']} FROM currency WHERE Date = ?", (row["published_at"][:7],))
        result = row["salary"] * float(cur.fetchone()[0])
        return round(result, 2)
    return row["salary"]


def currency_converter(filename):
    """Обрабатывает данные из колонок salary_from, salary_to, salary_currency и объединяет в колонку salary
    Args:
        filename: Путь к файлу vacancies_dif_currencies.csv
    """
    df = pd.read_csv(filename)
    df["salary"] = df.apply(lambda row: get_avg_salary(row), axis=1)
    df["salary"] = df.apply(lambda row: converter_salaries_in_rubles(row), axis=1)
    df.drop(labels=["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
    df = df[["name", "salary", "area_name", "published_at"]]
    cnx = sqlite3.connect("vacan.db")
    df.to_sql("vacan", con=cnx, index=False)


currency_converter('Data/vacancies_dif_currencies.csv')