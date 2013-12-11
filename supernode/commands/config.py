"""
Collects and stores the configuration information needed to use other commands.

Usage:
    supernode config [options]
    supernode config -h | --help

Options:
    --email <email>             The user e-mail address
    --insecure                  Disables HTTPS certificate validation
    --password <password>       The user password
    --partnerid <partnerid>     The partner ID
    --url <url>                 The REST API URL
                                    [default: https://manifests.reloadedtech.com]

If passed all options, the configuration will be validated and saved.
Otherwise, you will be prompted for the missing configuration information.

Configurations are stored in your home folder under the file: ~/.package.config
"""

from supernode.command import Command
import getpass


class ConfigCommand(Command):
    #noinspection PyMissingConstructor
    def __init__(self):
        self.api = None
        self.settings = {}

    def help(self):
        return __doc__

    def run(self, options):
        email = options['--email']
        password = options['--password']
        url = options['--url']
        verify = not options['--insecure']

        if email is None:
            email = raw_input('E-mail: ')

        if password is None:
            password = getpass.getpass()

        self.settings = {
            'email': email,
            'password': password,
            'url': url,
            'verify': str(verify)
        }

        self.load_api()

        print 'Validating credentials...'
        partners = self.api.get_user_partners()
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
                print '{0}. {1}'.format(i + 1, partners[i]['Name'])

            print ''
            i = int(raw_input('Please enter the number of the partner: ')) - 1
            partner_id = partners[i]['PartnerId']

        self.settings['partner_id'] = partner_id

        print 'Saving configuration...'
        self.save_settings()