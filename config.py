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

from collections import namedtuple
from docopt import docopt
import ConfigParser
import getpass
import os
import requests


class ConfigCommand:

    def __init__(self):
        pass

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
        partners = self.get_partners(email, password, url)
        partner_id = options['--partnerid']
        partner_ids = [p.PartnerId for p in partners]

        if partner_id in partner_ids:
            pass

        elif partners.__len__ == 1:
            partner_id = partners[0].PartnerId
            print 'Automatically using the only partner available:  {0}'.format(partner_id)

        elif partners.__len__ == 0:
            exit('No partners were found. Please contact technical support for assistance.')

        else:
            print 'Multiple partners were found. Please select one from the following:'
            print ''

            for i in range(len(partners)):
                print '{0}. {1}'.format(i, partners[i].Name)

            print ''
            i = int(raw_input('Please enter the number of the partner: '))
            partner_id = partners[i].PartnerId

        print 'Saving configuration...'
        self.save(email, password, url, partner_id)

    @staticmethod
    def get_partners(email, password, url):
        """
        Validates the configuration by returning a list of partners
        """
        response = requests.get('{0}/users/current/partners'.format(url), auth=(email, password))

        if response.status_code != 200:
            exit('Failure validating credentials')

        partner = namedtuple('Partner', 'PartnerId Name')
        return [partner(p['PartnerId'], p['Name']) for p in response.json()]

    @staticmethod
    def save(email, password, url, partner_id):
        """
        Saves the configuration settings to the ~/package.config file
        """
        path = '~/package.config'
        full_path = os.path.expanduser(path)

        parser = ConfigParser.SafeConfigParser(allow_no_value=True)
        parser.read(full_path)
        parser.set(None, 'email', email)
        parser.set(None, 'password', password)
        parser.set(None, 'url', url)
        parser.set(None, 'partner_id', partner_id)

        with open(full_path, 'wb') as f:
            parser.write(f)

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = ConfigCommand()
    command.run(args)