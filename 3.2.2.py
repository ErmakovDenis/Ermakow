import multiprocessing
import cProfile
import os
import pandas

list_print1 = ['Динамика уровня зарплат по годам: ','Динамика количества вакансий по годам: ',
                      'Динамика уровня зарплат по годам для выбранной профессии: ','Динамика количества вакансий по годам для выбранной профессии: ',
                      'Уровень зарплат по городам (в порядке убывания): ','Доля вакансий по городам (в порядке убывания): ']

class Solution:
    """Класс для получения и печати статистик
    Attributes:
        path_to_file (str): Путь к входному csv-файлу
        name_vacancy (str): Название выбранной профессии
        stats1 (dict): Динамика уровня зарплат по годам
        stats2 (dict): Динамика количества вакансий по годам
        stats3 (dict): Динамика уровня зарплат по годам для выбранной профессии
        stats4 (dict): Динамика количества вакансий по годам для выбранной профессии
        stats5 (dict): Уровень зарплат по городам (в порядке убывания)
        stats6 (dict): Доля вакансий по городам (в порядке убывания)
    """
    def __init__(self, path_to_file, name_vacancy):
        """Инициализирует объект Solution.
        Args:
            name_vacancy (str): Название выбранной профессии
            path_to_file (str): Путь к входному csv-файлу
        """
        self.path = path_to_file
        self.name_vacancy = name_vacancy
        self.stats1 = {}
        self.stats2 = {}
        self.stats3 = {}
        self.stats4 = {}
        self.stats5 = {}
        self.stats6 = {}

    def split_by_year(self):
        """Разделяет входной файл на меньшие, группирует по годам
        """
        df = pandas.read_csv(self.path)
        df["year"] = df["published_at"].apply(lambda x: x[:4])
        df = df.groupby("year")
        for y, info in df:
            info[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]]. \
                to_csv(rf"Data\info_by_years\{y}_year.csv", index=False)

    def get_stats(self):
        """Получение статистики
        """
        self.get_stats_by_year_with_multiprocessing()
        self.get_stats_by_city()

    def get_statistic_by_year(self, file_csv):
        """Составляет статистику по году
        Args:
            file_csv (str): Название файла с данными о вакансиях за год
        Returns:
            str, [int, int, int, int]: год, [ср. зп, всего вакансий, ср. зп для профессии, вакансий по профессии]
        """
        df = pandas.read_csv(file_csv)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["published_at"] = df["published_at"].apply(lambda s: int(s[:4]))
        info_of_file_vacancy = df[df["name"].str.contains(self.name_vacancy)]

        return df["published_at"].values[0], [int(df["salary"].mean()), len(df),
                                              int(info_of_file_vacancy["salary"].mean() if len(info_of_file_vacancy) != 0 else 0), len(info_of_file_vacancy)]

    def add_elements_to_stats(self, result):
        """Добавляет значения в статистику по годам
        Args:
            result (list): Список значений для статистики
        """
        for y, data_stats in result:
            self.stats1[y] = data_stats[0]
            self.stats2[y] = data_stats[1]
            self.stats3[y] = data_stats[2]
            self.stats4[y] = data_stats[3]

    def get_stats_by_year_not_with_multiprocessing(self):
        """Получает статистики по годам с использованием только одиного процесса
        """
        result = []
        for filename in os.listdir("Data/info_by_years"):
            with open(os.path.join("Data/info_by_years", filename), "r") as file_csv:
                result.append(self.get_statistic_by_year(file_csv.name))

        self.add_elements_to_stats(result)

    def get_stats_by_year_with_multiprocessing(self):
        """Получает статистики по годам с использованием нескольких процессов
        """
        files = [rf"Data/info_by_years\{file_name}" for file_name in os.listdir(rf"Data/info_by_years")]
        pool = multiprocessing.Pool(4)
        result = pool.starmap(self.get_statistic_by_year, [(file,) for file in files])
        pool.close()

        self.add_elements_to_stats(result)

    def get_stats_by_city(self):
        """Получает статистики по городам
        """
        df = pandas.read_csv(self.path_to_file)
        total = len(df)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["count"] = df.groupby("area_name")["area_name"].transform("count")
        df = df[df["count"] > total * 0.01]
        df = df.groupby("area_name", as_index=False)
        df = df[["salary", "count"]].mean().sort_values("salary", ascending=False)
        df["salary"] = df["salary"].apply(lambda s: int(s))

        self.stats5 = dict(zip(df.head(10)["area_name"], df.head(10)["salary"]))

        df = df.sort_values("count", ascending=False)
        df["count"] = round(df["count"] / total, 4)

        self.stats6 = dict(zip(df.head(10)["area_name"], df.head(10)["count"]))

    def print_statistic(self):
        """Выводит всю статистику с описанием
        Prints:
            Печатает каждую статистику с описанием
        """
        list_print2 = [self.stats1, self.stats2, self.stats3, self.stats4, self.stats5, self.stats6]
        for i in range(len(list_print1)):
            print(list_print1[i] + '{0}'.format(list_print2[i]))


if __name__ == '__main__':
    # solve = Solution(input("Введите название файла: "), input("Введите название профессии: "))
    # solve.split_by_year()
    # solve.get_stats()
    # solve.print_statistic()

    solve = Solution("Data/vacancies_by_year.csv", "Аналитик")
    solve.split_by_year()
    # cProfile.run("solve.get_stats_by_year_not_with_multiprocessing()", sort="cumtime")
    cProfile.run("solve.get_stats_by_year_with_multiprocessing()", sort="cumtime")