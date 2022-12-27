import requests
import time
import pandas as pd
import json


def get_page(num_of_page, second_part_of_day):
    """Получает ответ на запрос с api.hh.ru по сто вакансий за страницу
    Args:
        num_of_page (int): Номер страницы для выгрузки
        second_part_of_day (int): Вакансии во второй половине дня
    Returns:
        str: Список IT-вакансий в формате .json
    """
    if not second_part_of_day:
        parameters = {
            "specialization": 1,
            "found": 1,
            "per_page": 100,
            "page": num_of_page,
            "date_from": "2022-12-25T00:00:00+0300",
            "date_to": "2022-12-25T11:59:00+0300"
        }
    else:
        parameters = {
            "specialization": 1,
            "found": 1,
            "per_page": 100,
            "page": num_of_page,
            "date_from": "2022-12-25T12:00:00+0300",
            "date_to": "2022-12-25T23:59:00+0300"
        }
    try:
        request = requests.get('https://api.hh.ru/vacancies', parameters)
        info = request.content.decode()
        request.close()
    except:
        print("Неуспешный запрос")
        return get_page(num_of_page)

    print("Успешный запрос")
    return info


def set_vacancies():
    """Собирает и сохраняет в csv-файл данные о вакансиях с api.hh.ru
    """
    df = pd.DataFrame(columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    result = []
    for half in range(2):
        for page in range(0, 999):
            js_obj = json.loads(get_page(page, half))
            result.append(js_obj)
            if (js_obj['pages'] - page) <= 1:
                break
            time.sleep(1)

    for vac in result:
        for r in vac['items']:
            if r['salary'] is not None:
                df.loc[len(df)] = [r['name'], r['salary']['from'],
                                   r['salary']['to'], r['salary']['currency'],
                                   r['area']['name'], r['published_at']]
            else:
                df.loc[len(df)] = [r['name'], None,
                                   None, None,
                                   r['area']['name'], r['published_at']]

    df.to_csv("HHru_vacancies.csv", index=False)


set_vacancies()