import pandas as pd
from math import isnan

def converting_salaries_in_rubles(row):
    """Переводит значение salary в рубли после сравнения даты появления вакансии
    с датой в файле currency.csv
    Args:
        row (Series): Строка в data_file
    Returns:
        float: Значение для ячейки 'salary' в рублях
    """
    converter = pd.read_csv("currency.csv")
    if row["salary_currency"] in converter.columns:
        answer = row["salary"] * float(converter[converter["date"] == row["published_at"][:7]][row["salary_currency"]])
        return round(answer, 2)
    return row["salary"]


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


def get_conversion(filename):
    """Обрабатывает данные из колонок salary_from, salary_to, salary_currency и объединяет в колонку salary
    Args:
        filename: Путь к файлу vacancies_dif_currencies.csv
    """
    data_file = pd.read_csv(filename)
    result = data_file.loc[0:99].copy()
    result["salary"] = result.apply(lambda r: get_avg_salary(r), axis=1)
    result["salary"] = result.apply(lambda r: converting_salaries_in_rubles(r), axis=1)
    result.drop(labels=["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
    result = result[["name", "salary", "area_name", "published_at"]]
    result.to_csv("100_vac.csv", index=False)


get_conversion('Data/vacancies_dif_currencies.csv')