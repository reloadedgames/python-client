"""
Creates a new package.

Usage:
    create.py --path <path> --run <run> --name <name>
        [--arguments <args>] [--chunk-size 1048576]
        [--type package] [--version-name <name>]
    create.py -h | --help

Options:
    --arguments <args>      The arguments to pass to the file being run
    --chunk-size <size>     The chunk size in bytes [default: 1048576]
    --name <name>           The name of the package
    --path <path>           The path to the package files
    --run <run>             The path of the file to run for the package
    --type <type>           The type of package [default: package]
    --version-name <name>   The name of the package version
"""

from .update import UpdateCommand


class CreateCommand(UpdateCommand):
    def help(self):
        return __doc__

    def run(self, options):
        # Create the package
        print 'Creating new package...'
        name = options['--name']
        package_type = options['--type']
        package = self.api.create_package(self.settings['partner_id'], name, package_type)

        # Add to options and call the parent method
        options['--packageid'] = package['PackageId']
        return super(CreateCommand, self).run(options)