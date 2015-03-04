"""
Provides commands for creating and managing super node packages.

Usage:
    supernode <command> [<args>...]
    supernode <command> -h | --help
    supernode -h | --help

Commands:
    config      Collects configuration information needed to use other commands
    create      Creates a new package
    tag         Updates the specified version tag for a package
    update      Updates an existing package with a new version
    upload      Uploads the package contents to the S3 origin bucket
"""

from commands.config import ConfigCommand
from commands.create import CreateCommand
from commands.tag import TagCommand
from commands.update import UpdateCommand
from commands.upload import UploadCommand
from docopt import docopt


def main():
    args = docopt(__doc__, options_first=True)
    command_name = args['<command>'].lower()
    command = None
    options = [command_name] + args['<args>']

    if command_name == 'config':
        command = ConfigCommand()
    elif command_name == 'create':
        command = CreateCommand()
    elif command_name == 'tag':
        command = TagCommand()
    elif command_name == 'update':
        command = UpdateCommand()
    elif command_name == 'upload':
        command = UploadCommand()

    if command is None:
        exit('Invalid command')

    argv = docopt(command.help(), argv=options)
    command.run(argv)

if __name__ == '__main__':
    main()