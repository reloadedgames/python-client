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
from rest import RestApi


class CompleteCommand:
    def __init__(self):
        self._settings = ConfigCommand.load()
        self.rest = RestApi(self._settings['url'], self._settings['email'], self._settings['password'])

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
        self.rest.set_version(self._settings['package_id'], version_id)

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = CompleteCommand()
    command.run(args)