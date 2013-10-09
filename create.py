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

from docopt import docopt
from update import UpdateCommand


class CreateCommand(UpdateCommand):
    def run(self, options):
        """
        Executes the command

        @param options: The command-line options
        @type options: dict
        """

        # Create the package
        print 'Creating new package...'
        name = options['--name']
        package_type = options['--type']
        package = self.rest.create_package(self._settings['partner_id'], name, package_type)

        # Add to options and call the parent method
        options['--packageid'] = package['PackageId']
        return super(CreateCommand, self).run(options)

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = CreateCommand()
    command.run(args)