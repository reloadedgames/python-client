"""
Provides a command-line interface for creating and updating packages.

Usage:
    package [--config=<path>]
            <command> [options] [<args>...]
    package [--help]

Options:
    --config=<path>     The path to the config file

Commands include:
    checksum    Performs checksum calculations on package files
    config      Configures the package environment
    create      Creates a new package
    help        Displays help information for a specific command
    launch      Launches a new version of a package
    update      Creates a new package version
    upload      Uploads package files

See 'package help <command>' for more information on a specific command.
"""

from docopt import docopt
import sys

commands = ['checksum', 'config', 'create', 'launch', 'update', 'upload']

def example(args):
    """

    """
    print args
    exit()

if __name__ == '__main__':
    args = docopt(__doc__)
    command = args['<command>']

    if command is None:
        print(__doc__.strip())
        exit()

    elif command in commands:
        i = sys.argv.index(command)
        sub_argv = sys.argv[i:]
        example(sub_argv)

    else:
        error = '"{0}" is not a valid command.'.format(command)
        exit(error)