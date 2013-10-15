"""
Sets the newly created version as the current package version.

Usage:
    complete.py [options]
    complete.py -h | --help

Options:
    --versionid <versionid>      The version to set as current
"""

from supernode.command import Command


class CompleteCommand(Command):
    def help(self):
        return __doc__

    def run(self, options):
        if ('package_id', 'version_id') <= self.settings.keys():
            exit('The current saved configuration does not support updating the current version')

        version_id = self.settings['version_id']

        if options['--versionid'] is not None:
            version_id = options['--versionid']

        print 'Updating the current package version to {0}...'.format(version_id)
        self.api.set_version(self.settings['package_id'], version_id)