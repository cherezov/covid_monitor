# @file ru.py

from .BaseUpdater import BaseUpdater
from urllib.request import quote

class Updater(BaseUpdater):
    URL = 'http://xn--80aesfpebagmfblc0a.xn--p1ai/#operational-data'
    TEST_FILE = './ru/covid_ru.html'

    def __init__(self, src = URL):
        super(Updater, self).__init__('RU', '🇷🇺', src)

    def date(self):
        return date.today().strptime(date, '%d.%m.%Y')

    def total_tested(self):
        raw = self.html.xpath("//div[contains(@class, 'cv-countdown__item-value')]/span")[0].text
        # '>536 тыс'
        return int(raw.split()[0].strip(' <>')) * 1000

    def total_positive(self):
        raw = self.html.xpath("//div[contains(@class, 'cv-countdown__item-value')]/span")[1].text
        return int(raw.replace(' ', ''))

    def total_recovered(self):
        raw = self.html.xpath("//div[contains(@class, 'cv-countdown__item-value')]/span")[3].text
        return int(raw.replace(' ', ''))

    def total_dead(self):
        raw = self.html.xpath("//div[contains(@class, 'cv-countdown__item-value')]/span")[4].text
        return int(raw.replace(' ', ''))
