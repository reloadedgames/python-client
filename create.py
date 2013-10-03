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

from collections import namedtuple
from config import ConfigCommand
from docopt import docopt
import binascii
import os
import requests


class CreateCommand:
    def __init__(self):
        self._settings = ConfigCommand.load()

    def run(self, options):
        """
        Executes the command
        """

        # Read the package files and calculate their checksums
        print 'Processing package files...'
        path = options['--path']
        chunk_size = int(options['--chunk-size'])
        package_files = self.chunk_files(path, chunk_size)

        if not package_files:
            exit('The package directory contains no files')

        # Create the package
        print 'Creating the package...'
        name = options['--name']
        package_type = options['--type']
        package = self.create_package(name, package_type)

    def chunk_files(self, path, chunk_size):
        """
        Recursively reads all of the files in the specified path and returns a list of tuples
        representing them with their appropriate CRC values based on the chunk_size
        """
        if not os.path.isdir(path):
            exit('The path specified is not a directory')

        if type(chunk_size) is not int:
            exit("The chunk size must be an integer")

        if chunk_size < 1024 or chunk_size > 1073741824:
            exit("The chunk size must be between 1KB and 1GB")

        package_files = []
        package_file = namedtuple('PackageFile', 'Path Size Checksums')

        for root, dirs, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                file_path_relative = file_path.replace(path, '')
                size = os.path.getsize(file_path)
                checksums = self.calculate_checksums(file_path, chunk_size)

                package_files.append(package_file(file_path_relative, size, checksums))

        return package_files

    @staticmethod
    def calculate_checksums(path, chunk_size):
        """
        Returns the CRC values for each chunk of the specified file
        """
        checksums = []

        with open(path, 'r+b') as f:
            chunk = f.read(chunk_size)

            while chunk:
                checksums.append(binascii.crc32(chunk) & 0xffffffff)
                chunk = f.read(chunk_size)

        return checksums

    def create_package(self, name, package_type):
        """
        Creates the package through the REST API and returns its information
        """
        print self._settings
        return ''

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = CreateCommand()
    command.run(args)