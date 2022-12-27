import pandas as pd
import xmltodict
import requests

def get_currency(file_name):
    """Получает список валют, которые встречаются в более чем в 5000 вакансий
    Args:
        file_name (str): Путь к файлу vacancies_dif_currencies.csv
    Returns:
        list: Словарь валют
    """
    df = pd.read_csv(file_name)
    currency_dict = df['salary_currency'].value_counts().to_dict()
    currency_dict = {k: v for k, v in currency_dict.items() if v >= 5000}
    return currency_dict


def get_years_currency(file_name):
    """Собирает курсы валют за диапазон между самой старой и новой вакансией с частотностью раз в месяц,
     сохранет полученный результат (формат dataframe) в csv
    Args:
        file_name (str): Путь к файлу vacancies_dif_currencies.csv
    """
    df = pd.read_csv(file_name)
    res = pd.DataFrame()
    df = df[df["salary_currency"].isin(list(get_currency(file_name).keys()))]
    range_date = [df["published_at"].min().split("-")[:2], df["published_at"].max().split("-")[:2]]
    row = {}
    for y in range(int(range_date[0][0]), int(range_date[1][0]) + 1):
        for month in range(int(range_date[0][1]), 13):
            print(y, month)
            try:
                response = requests.get(fr"http://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{str(month).zfill(2)}/{y}")
            except Exception:
                continue

            response = xmltodict.parse(response.text)
            for i in response['ValCurs']['Valute']:
                if i['CharCode'] in list(get_currency(file_name).keys()):
                    row["date"] = f"{y}-{month}".zfill(2)
                    row[i['CharCode']] = round(float(i["Value"].replace(",", ".")) / int(i["Nominal"]), 7)
            res = pd.concat([res, pd.DataFrame([row])])
            if y == int(range_date[1][0]) and month == int(range_date[1][1]) or month == 12:
                break

    res.to_csv("currency.csv", index=False)

def info_by_year(path):
    """
    Группирует по годам
    Args:
        path (str): Путь к входному csv-файлу
    """
    df = pd.read_csv(path)
    df["year"] = df["published_at"].apply(lambda x: x[:4])
    df = df.groupby("year")
    for y, info in df:
        info[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].\
            to_csv(rf"Data\new_info_by_years\{y}_year.csv", index=False)


info_by_year("Data/vacancies_dif_currencies.csv")


get_years_currency('Data/vacancies_dif_currencies.csv')
