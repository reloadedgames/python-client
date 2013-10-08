"""
Collects and stores the configuration information needed to use other commands.

Usage:
    config.py [options]
    config.py -h | --help

Options:
    --email <email>             The user e-mail address
    --password <password>       The user password
    --partnerid <partnerid>     The partner ID
    --url <url>                 The REST API URL

If passed all options, the configuration will be validated and saved.
Otherwise, you will be prompted for the missing configuration information.

Configurations are stored in your home folder under the file: ~/.package.config
"""

from ConfigParser import SafeConfigParser
from docopt import docopt

import getpass
import os
from rest import RestApi


class ConfigCommand:

    # The full path for the config file
    _path = os.path.expanduser('~/package.config')

    def __init__(self):
        self.rest = None

    def run(self, options):
        """
        Executes the command
        """
        email = options['--email']
        password = options['--password']
        url = options['--url']

        if email is None:
            email = raw_input('E-mail: ')

        if password is None:
            password = getpass.getpass()

        if url is None:
            url = raw_input('URL: ')

        print 'Validating credentials...'
        self.rest = RestApi(url, email, password)

        partners = self.rest.get_user_partners()
        partner_id = options['--partnerid']
        partner_ids = [p['PartnerId'] for p in partners]

        if partner_id in partner_ids:
            pass

        elif partners.__len__ == 1:
            partner_id = partners[0]['PartnerId']
            print 'Automatically using the only partner available: {0}'.format(partner_id)

        elif partners.__len__ == 0:
            exit('No partners were found. Please contact technical support for assistance.')

        else:
            print 'Multiple partners were found. Please select one from the following:'
            print ''

            for i in range(len(partners)):
                print '{0}. {1}'.format(i, partners[i]['Name'])

            print ''
            i = int(raw_input('Please enter the number of the partner: '))
            partner_id = partners[i]['PartnerId']

        print 'Saving configuration...'
        self.save({
            'email': email,
            'password': password,
            'url': url,
            'partner_id': partner_id
        })

    @staticmethod
    def save(values):
        """
        Saves the configuration settings to the ~/package.config file
        """
        parser = SafeConfigParser(allow_no_value=True)

        for name, value in values.items():
            parser.set(None, name, value)

        with open(ConfigCommand._path, 'wb') as f:
            parser.write(f)

    @staticmethod
    def load():
        """
        Loads and returns all of the configuration settings
        """
        parser = SafeConfigParser(allow_no_value=True)
        parser.read(ConfigCommand._path)
        values = dict(parser.items('DEFAULT'))

        if not values:
            exit('No configuration settings could be read')

        return values

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = ConfigCommand()
    command.run(args)