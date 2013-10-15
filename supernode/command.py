from api import RestApi
from .config import *


class Command(object):
    def __init__(self):
        self.settings = {}
        self.api = None
        self.load_settings()
        self.load_api()

    def load_api(self):
        self.api = RestApi(self.settings)

    def load_settings(self):
        self.settings = Config.load()

    def save_settings(self):
        Config.save(self.settings)

    def help(self):
        pass

    def run(self, options):
        pass