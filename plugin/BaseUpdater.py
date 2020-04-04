# @file BaseUpdater.py

import os
from lxml import html
import urllib.request
import ssl

class BaseUpdater:
    def __init__(self, name, flag, src):
        self.name = name.lower() 
        self.src = src
        self.flag = flag
        self.html = None
        self.update()

    def update(self):
        if os.path.isfile(self.src):
            with open(self.src, 'r', encoding='utf8') as f:
                self.html = html.parse(f)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self.html =  html.parse(urllib.request.urlopen(self.src, context=ctx))

    def date(self):
        pass

    def total_tested(self):
        pass

    def total_positive(self):
        pass

    def total_recovered(self):
        pass

    def total_dead(self):
        pass

