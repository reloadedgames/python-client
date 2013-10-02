from config import Config
from pprint import pprint


if __name__ == '__main__':
    config = Config()
    config.email = 'lance@mcnearney.net'
    config.password = 'testpass1'
    config.url = 'https://manifests.reloadedtech.com'
    config.save()

    pprint(vars(config))