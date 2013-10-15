from ConfigParser import SafeConfigParser
import os

CONFIG_PATH = os.path.expanduser('~/package.config')


class Config(object):
    @staticmethod
    def save(values):
        """
        Saves the configuration settings to the ~/package.config file
        """
        parser = SafeConfigParser()

        for name, value in values.items():
            parser.set(None, name, value)

        with open(CONFIG_PATH, 'wb') as f:
            parser.write(f)

    @staticmethod
    def load():
        """
        Loads and returns all of the configuration settings
        """
        parser = SafeConfigParser()
        parser.read(CONFIG_PATH)
        values = dict(parser.items('DEFAULT'))

        if not values:
            raise Exception('No configuration settings could be read')

        return values