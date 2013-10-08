"""
Sets the newly created version as the current package version.

Usage:
    complete.py [options]
    complete.py -h | --help

Options:
    --versionid <versionid>      The version to set as current
"""

from config import ConfigCommand
from docopt import docopt
import requests


class CompleteCommand:
    def __init__(self):
        self._settings = ConfigCommand.load()

        # Validate settings
        if ('package_id', 'version_id') <= self._settings.keys():
            exit('The current saved configuration does not support updating the current version')

    def run(self, options):
        """
        Executes the command

        @param options: The incoming command-line options
        @type options: dict
        """
        version_id = self._settings['version_id']

        if options['--versionid'] is not None:
            version_id = options['--versionid']

        print 'Updating the current package version to {0}...'.format(version_id)
        self.set_version(version_id)

    def set_version(self, version_id):
        """
        Sends the API request updating the package version

        @param version_id: The primary key of the version
        @type version_id: string
        """
        settings = self._settings
        url = '{0}/packages/{1}'.format(settings['url'], settings['package_id'])
        credentials = (settings['email'], settings['password'])
        parameters = {
            'VersionId': version_id
        }

        response = requests.put(url, auth=credentials)

        if response.status_code != 200:
            exit('There was a problem updating the current version')


# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = CompleteCommand()
    command.run(args)