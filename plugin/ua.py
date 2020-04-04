# @file ua.py

from .BaseUpdater import BaseUpdater
from urllib.request import quote

class Updater(BaseUpdater):
    URL = 'https://covid19.com.ua/en'
    TEST_FILE = ''

    def __init__(self, src = URL):
        super(Updater, self).__init__('UA', '🇺🇦', src)

    def date(self):
        return date.today().strptime(date, '%d.%m.%Y')

    def total_tested(self):
        raw = self.html.xpath("//div[contains(@class, 'field-value')]")[0].text
        return int(raw.split()[0].strip(' <>'))

    def total_positive(self):
        raw = self.html.xpath("//div[contains(@class, 'field-value')]")[1].text
        return int(raw.replace(' ', ''))

    def total_recovered(self):
        raw = self.html.xpath("//div[contains(@class, 'field-value')]")[2].text
        return int(raw.replace(' ', ''))

    def total_dead(self):
        raw = self.html.xpath("//div[contains(@class, 'field-value')]")[3].text
        return int(raw.replace(' ', ''))
