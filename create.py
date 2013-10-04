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

        # Create the version
        print 'Creating an initial version...'
        arguments = options['--arguments']
        package_id = package['PackageId']
        path_absolute = os.path.abspath(path)
        run_path = os.path.abspath(options['--run'])
        run_relative_path = run_path.replace(path_absolute, '').lstrip('/\\')
        version_name = options['--version-name']
        version = self.create_version(package_id, run_relative_path, arguments, version_name)
        version_id = version['VersionId']

        # Add files
        print 'Adding files to version...'

        for f in package_files:
            print '  {0}'.format(f.Path)
            self.add_file(version_id, f, chunk_size)

        # Complete the version
        print 'Marking the version as complete...'
        self.complete_version(version_id)

        print 'Saving package information to configuration...'
        self._settings['package_id'] = package_id
        self._settings['version_id'] = version_id
        self._settings['path'] = path_absolute
        ConfigCommand.save(self._settings)

        print 'Package complete.'
        print ''
        print 'PackageId = {0}'.format(package_id)
        print 'VersionId = {0}'.format(version_id)

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
                file_path_relative = file_path.replace(path, '').lstrip('/\\')
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
        settings = self._settings
        url = '{0}/packages'.format(settings['url'])
        credentials = (settings['email'], settings['password'])
        parameters = {
            'Name': name,
            'PartnerId': settings['partner_id'],
            'Type': package_type
        }

        response = requests.post(url, parameters, auth=credentials)

        if response.status_code != 200:
            exit('There was a problem creating the package')

        return response.json()

    def create_version(self, package_id, run, arguments=None, name=None):
        """
        Creates the package version and returns its information
        """
        settings = self._settings
        url = '{0}/packages/{1}/versions'.format(settings['url'], package_id)
        credentials = (settings['email'], settings['password'])
        parameters = {
            'Arguments': arguments,
            'Name': name,
            'Run': run
        }

        version = requests.post(url, parameters, auth=credentials)

        if version.status_code != 200:
            exit('There was a problem creating the version')

        return version.json()

    def add_file(self, version_id, package_file, chunk_size):
        """
        Adds the file to the package version
        """
        settings = self._settings
        url = '{0}/versions/{1}/files'.format(settings['url'], version_id)
        credentials = (settings['email'], settings['password'])
        parameters = {
            'Checksums': ','.join(str(i) for i in package_file.Checksums),
            'Chunk': chunk_size,
            'Path': package_file.Path,
            'Size': package_file.Size
        }

        response = requests.post(url, parameters, auth=credentials)

        if response.status_code != 200:
            exit('There was a problem adding the file to the version')

    def complete_version(self, version_id):
        """
        Marks the version as complete after all of the files have been added
        """
        settings = self._settings
        url = '{0}/versions/{1}/complete'.format(settings['url'], version_id)
        credentials = (settings['email'], settings['password'])

        response = requests.post(url, auth=credentials)

        if response.status_code != 200:
            exit('There was a problem marking the version as complete')

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = CreateCommand()
    command.run(args)