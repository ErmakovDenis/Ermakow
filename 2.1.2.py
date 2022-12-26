import csv
import math
import matplotlib.pyplot as plt
import numpy as np

name_list = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]

list_print1 = ['Динамика уровня зарплат по годам: ', 'Динамика количества вакансий по годам: ',
               'Динамика уровня зарплат по годам для выбранной профессии: ',
               'Динамика количества вакансий по годам для выбранной профессии: ',
               'Уровень зарплат по городам (в порядке убывания): ', 'Доля вакансий по городам (в порядке убывания): ']

currency_to_rub = {"KZT": 0.13, "RUR": 1, "AZN": 35.68, "GEL": 21.74, "UZS": 0.0055,
                   "KGS": 0.76, "UAH": 1.64, "BYR": 23.91, "EUR": 59.90, "USD": 60.66}


class Vacancy:
    """Класс для получения данных о вакансии.

    Attributes:
        name (str): Название вакансии
        salary_average (int): Средняя зарплата в рублях
        area_name (str): Название города
        publication_year (int): Год публикации вакансии
    """

    def __init__(self, vacancies):
        """Инициализирует объект Vacancy, вычисляет среднюю зарплату и переводит в рубли

        Args:
            vacancies (dict): Вакансия
        """
        self.name = vacancies[name_list[0]]
        self.salary_average = math.floor((float(vacancies[name_list[1]]) + float(vacancies[name_list[2]])) / 2) \
                              * currency_to_rub[vacancies[name_list[3]]]
        self.area_name = vacancies[name_list[4]]
        self.publication_year = int(vacancies[name_list[5]][:4])


class DataSet:
    """Класс для получения и печати статистик.

    Attributes:
        filename (str): Название файла с данными о вакансиях
        vacancy_name (str): Название выбранной профессии
    """

    def __init__(self, filename, vacancy_name):
        """Инициализирует объект DataSet.

        Args:
            filename (str): Название файла с данными о вакансиях
            vacancy_name (str): Название выбранной профессии
        """
        self.filename, self.vacancy_name = filename, vacancy_name

    def csv_reader(self):
        """Считывает данные из входного файла

        Returns:
            dict: Все вакансии с информацией о них.
        """
        with open(self.filename, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            header_length = len(header)
            for row in reader:
                if '' not in row and len(row) == header_length:
                    yield dict(zip(header, row))

    @staticmethod
    def average(dict):
        """Высчитывает среднее значение.

        Args:
            dict (dict): Словарь с значениями
        Returns:
            dict: Словарь с обновленными, средними значениями
        """
        new_dict = {}
        for k, v in dict.items():
            new_dict[k] = int(sum(v) / len(v))
        return new_dict

    @staticmethod
    def increment(dict, k, с):
        """Дополняет словарь всех средних зарплат за год или в городе

        Args:
            dict (dict): Словарь со всеми зарплатами за год или в городе по вакансии
            k (int): Год или город вакансии, по которому идет подсчет
            с (list): Средняя зарплата у вакансии
        """
        if k in dict:
            dict[k] += с
        else:
            dict[k] = с

    def get_dynamics(self):
        """Получает все необходимые статистики для дальнейшей работы

        Returns:
            dict, dict, dict, dict, dict, dict: Все необходимые статистики
        """
        salary = {}
        salary_of_name = {}
        city = {}
        count = 0

        for vacancy_dictionary in self.csv_reader():
            vacancy = Vacancy(vacancy_dictionary)
            self.increment(salary, vacancy.publication_year, [vacancy.salary_average])
            if vacancy.name.find(self.vacancy_name) != -1:
                self.increment(salary_of_name, vacancy.publication_year, [vacancy.salary_average])
            self.increment(city, vacancy.area_name, [vacancy.salary_average])
            count += 1

        number = dict([(k, len(v)) for k, v in salary_of_name.items()])
        vacancy_number = dict([(k, len(v)) for k, v in salary.items()])

        if not salary_of_name:
            number = dict([(k, 0) for k, v in vacancy_number.items()])
            salary_of_name = dict([(k, [0]) for k, v in salary.items()])

        dynamics1, dynamics2, dynamics3 = self.average(salary), self.average(salary_of_name), self.average(city)

        dynamics4 = {}
        for y, s in city.items():
            dynamics4[y] = round(len(s) / count, 4)
        dynamics4 = list(filter(lambda x: x[-1] >= 0.01, [(k, v) for k, v in dynamics4.items()]))
        dynamics4.sort(key=lambda x: x[-1], reverse=True)
        dynamics5 = dict(dynamics4.copy()[:10])
        dynamics4 = dict(dynamics4)
        dynamics3 = list(filter(lambda x: x[0] in list(dynamics4.keys()), [(k, v) for k, v in dynamics3.items()]))
        dynamics3.sort(key=lambda x: x[-1], reverse=True)
        dynamics3 = dict(dynamics3[:10])

        return dynamics1, vacancy_number, dynamics2, number, dynamics3, dynamics5

    @staticmethod
    def print_statistic(dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6):
        """Выводит все динамики с описанием

        Args:
            dynamics1 (dict): Динамика уровня зарплат по годам
            dynamics2 (dict): Динамика количества вакансий по годам
            dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
            dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
            dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
            dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
        Prints:
            Печатать каждой динамики с описанием
        """
        list_print2 = [dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6]
        for i in range(len(list_print1)):
            print(list_print1[i] + '{0}'.format(list_print2[i]))


class InputConnect:
    """Класс для получения объектов DataSet и Report.

    Attributes:
        filename (str): Название файла с данными о вакансиях
        name_vacancy (str): Название выбранной профессии
    """

    def __init__(self):
        """Инициализирует объект InputConnect.
        """
        self.filename, self.name_vacancy = input('Введите название файла: '), input('Введите название профессии: ')

        dataset = DataSet(self.filename, self.name_vacancy)
        dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6 = dataset.get_dynamics()
        dataset.print_statistic(dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6)

        report = Report(self.name_vacancy, dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6)
        report.generate_image()


class Report:
    """Класс для получения отчета по полученным динамикам.

    Attributes:
        name_vacancy (str): Название выбранной профессии
        dynamics1 (dict): Динамика уровня зарплат по годам
        dynamics2 (dict): Динамика количества вакансий по годам
        dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
        dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
        dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
        dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
    """

    def __init__(self, name_vacancy, dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6):
        """Инициализирует объект Report.

        Args:
            name_vacancy (str): Название выбранной профессии
            dynamics1 (dict): Динамика уровня зарплат по годам
            dynamics2 (dict): Динамика количества вакансий по годам
            dynamics3 (dict): Динамика уровня зарплат по годам для выбранной профессии
            dynamics4 (dict): Динамика количества вакансий по годам для выбранной профессии
            dynamics5 (dict): Уровень зарплат по городам (в порядке убывания)
            dynamics6 (dict): Доля вакансий по городам (в порядке убывания)
        """
        self.name_vacancy = name_vacancy
        self.dynamics1, self.dynamics2, self.dynamics3, self.dynamics4, self.dynamics5, self.dynamics6 \
            = dynamics1, dynamics2, dynamics3, dynamics4, dynamics5, dynamics6

    def generate_image(self):
        """Генерирует 4 диаграммы в на одной старнице на основе статистик, после чего сохраняет картинку в файл graph.png
        """
        x = np.arange(len(self.dynamics1.keys()))
        width = 0.35

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(ncols=2, nrows=2)
        ax1.bar(x - width / 2, self.dynamics1.values(), width, label='средняя з/п')
        ax1.bar(x + width / 2, self.dynamics3.values(), width, label='з/п {0}'.format(self.name_vacancy))
        plt.rcParams['font.size'] = '8'
        ax1.set_title('Уровень зарплат по годам')
        ax1.set_xticks(x, self.dynamics1.keys(), rotation=90)
        ax1.legend(fontsize=8)
        ax1.grid(axis='y')

        ax2.bar(x - width / 2, self.dynamics2.values(), width, label='количество вакансий')
        ax2.bar(x + width / 2, self.dynamics4.values(), width,
                label='количество вакансий {0}'.format(self.name_vacancy))
        ax2.set_xticks(x, self.dynamics2.keys(), rotation=90)
        ax2.set_title('Количество вакансий по годам')
        ax2.legend(fontsize=8)
        ax2.grid(axis='y')
        fig.tight_layout()

        areas = []
        for area in self.dynamics5.keys():
            areas.append(str(area).replace(' ', '\n').replace('-', '-\n'))
        y_pos = np.arange(len(areas))
        performance = self.dynamics5.values()
        error = np.random.rand(len(areas))
        ax3.barh(y_pos, performance, xerr=error, align='center')
        ax3.set_title('Уровень зарплат по городам')
        ax3.set_yticks(y_pos, labels=areas, size=6)
        ax3.invert_yaxis()
        ax3.grid(axis='x')

        val = list(self.dynamics6.values()) + [1 - sum(list(self.dynamics6.values()))]
        k = list(self.dynamics6.keys()) + ['Другие']
        ax4.pie(val, labels=k, startangle=170)
        ax4.set_title('Доля вакансий по городам')
        plt.tight_layout()
        plt.savefig('graph.png', dpi=300)


if __name__ == '__main__':
    InputConnect()