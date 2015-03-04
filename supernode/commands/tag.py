"""
Updates the specified version tag for a package.

Usage:
    supernode tag --tag <tag>
        [--delete] [--packageid <packageid>]
        [--versionid <versionid>]
    supernode tag -h | --help

Options:
    --delete                    Delete the specified tag
    --packageid <packageid>     The package being updated
    --tag <tag>                 The name of the tag
    --versionid <versionid>     The version being set for the tag
"""

from supernode.command import Command


class TagCommand(Command):
    def help(self):
        return __doc__

    def run(self, options):
        package_id = options['--packageid'] or self.settings['package_id']
        version_id = options['--versionid'] or self.settings['version_id']

        if package_id is None or version_id is None:
            exit('The current saved configuration does not support updating a tag')

        tag = options['--tag']

        # Validate the tag exists for the partner
        available_tags = self.api.get_tags(package_id)

        if tag not in available_tags:
            exit('The package tag specified is invalid')

        if not options['--delete']:
            print 'Setting package tag...'
            self.api.set_tag(package_id, tag, version_id)
            return

        print 'Deleting package tag...'
        self.api.remove_tag(package_id, tag)