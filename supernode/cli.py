"""
Provides commands for creating and managing super node packages.

Usage:
    cli.py <command> [<args>...]
    cli.py <command> -h | --help
    cli.py -h | --help

Commands:
    complete    Sets the newly created version as the current package version
    config      Collects configuration information needed to use other commands
    create      Creates a new package
    update      Updates an existing package with a new version
    upload      Uploads package contents to the SFTP infrastructure
"""

from commands.complete import CompleteCommand
from commands.config import ConfigCommand
from commands.create import CreateCommand
from commands.update import UpdateCommand
from commands.upload import UploadCommand
from docopt import docopt


def main():
    args = docopt(__doc__, options_first=True)
    command_name = args['<command>'].lower()
    command = None
    options = args['<args>']

    if command_name == 'complete':
        command = CompleteCommand()
    elif command_name == 'config':
        command = ConfigCommand()
    elif command_name == 'create':
        command = CreateCommand()
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