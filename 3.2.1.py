import pandas

pandas.set_option("display.max_columns", False)
pandas.set_option("expand_frame_repr", False)


def info_by_year(path):
    """
    Группирует по годам
    Args:
        path (str): Путь к входному csv-файлу
    """
    df = pandas.read_csv(path)
    df["year"] = df["published_at"].apply(lambda x: x[:4])
    df = df.groupby("year")
    for y, info in df:
        info[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].\
            to_csv(rf"Data\info_by_years\{y}_year.csv", index=False)


info_by_year("Data/vacancies_by_year.csv")