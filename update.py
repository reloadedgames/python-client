"""
Updates an existing package with a new version.

Usage:
    update.py --path <path> --run <run>
        [--arguments <args>] [--chunk-size 1048576]
        [--packageid <packageid>] [--type package]
        [--version-name <name>]
    update.py -h | --help

Options:
    --arguments <args>          The arguments to pass to the file being run
    --chunk-size <size>         The chunk size in bytes [default: 1048576]
    --packageid <packageid>     The package being updated
    --path <path>               The path to the package files
    --run <run>                 The path of the file to run for the package
    --version-name <name>       The name of the package version

If no package is specified, the command will update package_id stored in the
current configuration.
"""

from config import ConfigCommand
from docopt import docopt
from rest import RestApi
import binascii
import os


class UpdateCommand(object):
    def __init__(self):
        """
        Initializes the command
        """

        self._settings = ConfigCommand.load()
        self.rest = RestApi(self._settings)

    def run(self, options):
        """
        Executes the command

        @param options: The command-line options
        @type options: dict
        """

        # Which package is being updated?
        package_id = options['--packageid'] or self._settings['package_id']

        if package_id is None:
            exit('No package specified')

        # Read the package files and calculate their checksums
        print 'Processing package files...'
        path = options['--path']
        chunk_size = int(options['--chunk-size'])
        package_files = self.chunk_files(path, chunk_size)

        if not package_files:
            exit('The package directory contains no files')

        # Create the version
        print 'Creating new version...'
        arguments = options['--arguments']
        path_absolute = os.path.abspath(path)
        run_path = os.path.abspath(options['--run'])
        run_relative_path = run_path.replace(path_absolute, '').lstrip('/\\')
        version_name = options['--version-name']
        version = self.rest.create_version(package_id, run_relative_path, arguments, version_name)
        version_id = version['VersionId']

        # Add files
        print 'Adding files to version...'

        for f in package_files:
            print '  {0}'.format(f['path'])
            self.rest.add_file(version_id, f['path'], f['size'], chunk_size, f['checksums'])

        # Complete the version
        print 'Marking the version as complete...'
        self.rest.complete_version(version_id)

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

        @param path: The directory file path
        @type path: str
        @param chunk_size: The chunk file size
        @type chunk_size: int
        @rtype : list
        """
        if not os.path.isdir(path):
            exit('The path specified is not a directory')

        if type(chunk_size) is not int:
            exit("The chunk size must be an integer")

        if chunk_size < 1024 or chunk_size > 1073741824:
            exit("The chunk size must be between 1KB and 1GB")

        package_files = []

        for root, dirs, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                file_path_relative = file_path.replace(path, '').lstrip('/\\')
                size = os.path.getsize(file_path)
                checksums = self.calculate_checksums(file_path, chunk_size)

                package_files.append({
                    'path': file_path_relative,
                    'size': size,
                    'checksums': checksums
                })

        return package_files

    @staticmethod
    def calculate_checksums(path, chunk_size):
        """
        Returns the CRC values for each chunk of the specified file

        @param path: The path to the file
        @type path: str
        @param chunk_size: The file chunk size
        @type chunk_size: int
        @rtype : list
        """
        checksums = []

        with open(path, 'r+b') as f:
            chunk = f.read(chunk_size)

            while chunk:
                checksums.append(binascii.crc32(chunk) & 0xffffffff)
                chunk = f.read(chunk_size)

        return checksums

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = UpdateCommand()
    command.run(args)