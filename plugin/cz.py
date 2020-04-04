# @file cz.py

from .BaseUpdater import BaseUpdater

class Updater(BaseUpdater):
    URL = 'https://onemocneni-aktualne.mzcr.cz/covid-19'
    TEST_FILE = './cz/covid_cz.html'

    def __init__(self, src = URL):
        super(Updater, self).__init__('CZ', '🇨🇿', src)

    def date(self):
        # Posledni aktualizace: 23. 3. 2020 v 8.47h
        raw = self.html.xpath("//p[@id='last-modified-datetime']")[0].text

        dt = raw.split(':')[1].strip('h \n') # "23. 3. 2020 v 8.47"
        date, time = dt.split(' v ')         # "23. 3. 2020", "8.47"
        date = date.replace(' ', '')         # "23. 3. 2020" ->  "23.3.2020"
        time = time.replace('.', ':')        # "8.47" -> "8:47"

        #return datetime.strptime('{} {}'.format(date, time), '%d.%m.%Y %H:%M')
        return date.strptime(date, '%d.%m.%Y')

    def total_tested(self):
        raw = self.html.xpath("//p[@id='count-test']")[0].text
        return int(raw.replace(' ', ''))

    def total_positive(self):
        raw = self.html.xpath("//p[@id='count-sick']")[0].text
        return int(raw.replace(' ', ''))

    def total_recovered(self):
        raw = self.html.xpath("//p[@id='count-recover']")[0].text
        return int(raw.replace(' ', ''))

    def total_dead(self):
        raw = self.html.xpath("//p[@id='count-dead']")[0].text
        return int(raw.replace(' ', ''))
