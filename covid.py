# @file covid.py

import os
import csv
import json
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt

DATE_FMT = '%Y%d%m'
TIME_FMT = '%H:%M'

class DayStat:
    def __init__(self, date, tested = 0, positive = 0, recovered = 0, dead = 0):
        self.date = date
        self.tested = int(tested)
        self.positive = int(positive)
        self.recovered = int(recovered)
        self.dead = int(dead)

    @property
    def percent(self):
        if self.tested == 0:
            return 0
        return self.positive / self.tested * 100

    def today(self):
        self.date = date.today()
        return self

    def yesterday(self):
        self.date = date.today() - timedelta(days=1)
        return self

    def is_empty(self):
        return not (self.tested or self.positive or self.recovered or self.dead)

    def __add__(self, s):
        if not self.date == s.date:
            return self
        return DayStat(self.date, self.tested + s.tested, self.positive + s.positive, self.recovered + s.recovered, self.dead + s.dead)

    def __eq__(self, s):
        return self.date == s.date and self.tested == s.tested and self.positive == s.positive and self.dead == s.dead

    def __repr__(self):
        return '{}[(t){}, (p){}, (t/p){:.2f}%, (r){}, (d){}]'.format(self.date.strftime('%Y%b%d'), self.tested, self.positive, self.percent, self.recovered, self.dead)

class CovidStat:
    DATA_FILE_FMT = './data/covid_data_{}.csv'

    def __init__(self, updater):
        self.by_date = {}
        self.updater = updater

    def flag(self):
        return self.updater.flag

    def update(self):
        self.updater.update()

    def review_new_data(self):
        return DayStat(date.today(), self.delta_tested(), self.delta_positive(), self.delta_recovered(), self.delta_dead())

    def add_new_data(self, dayStat):
        if not dayStat.date in self.by_date:
            self.by_date[dayStat.date] = DayStat(dayStat.date)

        self.by_date[dayStat.date] += dayStat

    def load(self, from_file = DATA_FILE_FMT):
        self.by_date = {}
        from_file = from_file.format(self.updater.name)
        with open(from_file, 'r') as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                dayStat = dict(row)
                dt = datetime.strptime(dayStat['Date'], DATE_FMT).date()
                self.by_date[dt] = DayStat(dt, dayStat['Tested'], dayStat['Positive'], dayStat['Recovered'], dayStat['Dead'])

    def save(self, to_file = DATA_FILE_FMT):
        to_file = to_file.format(self.updater.name)
        with open(to_file, 'w') as f:
            header = ['Date', 'Tested', 'Positive', 'Recovered', 'Dead']
            f.write(','.join(header))
            f.write('\n')

            for date, d in self.by_date.items():
                f.write(','.join([date.strftime(DATE_FMT), str(d.tested), str(d.positive), str(d.recovered), str(d.dead)]))
                f.write('\n')

    def delta_tested(self):
        return self.updater.total_tested() - self.total_tested()

    def delta_positive(self):
        return self.updater.total_positive() - self.total_positive()

    def delta_recovered(self):
        return self.updater.total_recovered() - self.total_recovered()

    def delta_dead(self):
        return self.updater.total_dead() - self.total_dead()

    def total_tested(self):
        return sum([s.tested for date, s in self.by_date.items()])

    def total_positive(self):
        return sum([s.positive for date, s in self.by_date.items()])

    def total_recovered(self):
        return sum([s.recovered for date, s in self.by_date.items()])

    def total_dead(self):
        return sum([s.dead for date, s in self.by_date.items()])

    def __repr__(self):
        return 'CovidStat[\n{}\n]'.format(
            '\n'.join([str(stat) for date, stat in self.by_date.items()]))

    def save_plot(self, parameter = ['tested'], title = None):
        if not os.path.exists('plot'):
            os.makedirs('plot')
        file_name = 'plot/{}_{}.jpg'.format(parameter, date.today().strftime(DATE_FMT))

        by_date = dict(self.by_date)
        last_day = max(by_date.keys())
        if by_date[last_day].percent == 0:
            del by_date[max(by_date.keys())]

        for p in parameter:
            x = [d.strftime("%b%d") for d in by_date]
            if p.startswith('average'):
                p = p.split(':')[1]
                avg = sum([getattr(v, p) for date, v in by_date.items()]) / len(by_date)
                y = [avg for date, v in by_date.items()]
                p = 'average'
            else:
                y = [getattr(v, p) for date, v in by_date.items()]
            plt.plot(x, y, label=p)
        title = ' vs '.join(parameter) if title is None else title
        plt.title('{} {}'.format(self.updater.name.upper(), title))
        plt.xlabel('date')
        plt.legend(loc="upper left")
        plt.savefig(file_name)
        plt.clf()

        return file_name

def all_locales():
    import glob

    locales = []
    for f in glob.glob(os.path.join('plugin', '*.py')):
        fname = os.path.basename(f)
        if not fname == 'BaseUpdater.py':
            locales.append(os.path.splitext(fname)[0])
    return locales

def load_updater(locale):
    import importlib
    plugin = importlib.import_module('plugin.{}'.format(locale))
    return plugin.Updater(plugin.Updater.URL)

if __name__ == '__main__':
    import sys

    locales = all_locales()
    if len(sys.argv) == 1:
        print('{} <{}>'.format(sys.argv[0], '|'.join(locales)))
        exit(1)

    locale = sys.argv[1].lower()

    if locale not in locales:
        print('Unknown locale plugin: {}'.format(locale))
        exit(1)

    updater = load_updater(locale)
    s = CovidStat(updater)
    s.load()
    nd = s.review_new_data()
    print(nd)
