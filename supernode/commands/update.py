"""
Updates an existing package with a new version.

Usage:
    supernode update --path <path>
        [--arguments <args>] [--chunk-size 1048576]
        [--packageid <packageid>] [--run <run>]
        [--type package] [--version-name <name>]
    supernode update -h | --help

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

from supernode.command import Command
import binascii
import hashlib
import os


class UpdateCommand(Command):
    def help(self):
        return __doc__

    def run(self, options):
        # Which package is being updated?
        package_id = options['--packageid'] or self.settings['package_id']

        if package_id is None:
            exit('No package specified')

        # Validate package belongs to configured partner
        package = self.api.get_package(package_id)

        if package['PartnerId'] != self.settings['partner_id']:
            exit('The specified package does not belong to the currently configured partner')

        # Read the package files and calculate their checksums
        print 'Processing package files...'
        path_absolute = os.path.abspath(options['--path'])
        chunk_size = int(options['--chunk-size'])
        package_files = self.chunk_files(path_absolute, chunk_size)

        if not package_files:
            exit('The package directory contains no files')

        # Create the version
        print 'Creating new version...'
        arguments = options['--arguments']

        # Run is optional
        if options['--run'] is not None:
            run_path = os.path.abspath(options['--run'])

            if not os.path.isfile(run_path):
                exit('Run file specified does not exist')

            run_relative_path = run_path.replace(path_absolute, '').lstrip('/\\')
        else:
            run_relative_path = None

        version_name = options['--version-name']
        version = self.api.create_version(package_id, run_relative_path, arguments, version_name)
        version_id = version['VersionId']

        # Add files
        print 'Adding files to version...'

        for f in package_files:
            print '  {0}'.format(f['path'])
            self.api.add_file(version_id, f['path'], f['size'], chunk_size, f['checksums'], f['md5'])

        print 'Saving package information to configuration...'
        self.settings['package_id'] = package_id
        self.settings['version_id'] = version_id
        self.settings['path'] = path_absolute
        self.save_settings()

        print ''
        print 'PackageId = {0}'.format(package_id)
        print 'VersionId = {0}'.format(version_id)

    def chunk_files(self, path, chunk_size):
        """
        Recursively reads all of the files in the specified path and returns a list of tuples
        representing them with their appropriate CRC values based on the chunk_size

        @type path: str
        @type chunk_size: int
        @rtype: list of dict
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
                md5, checksums = self.calculate_checksums(file_path, chunk_size)

                package_files.append({
                    'md5': md5,
                    'path': file_path_relative,
                    'size': size,
                    'checksums': checksums
                })

        return package_files

    @staticmethod
    def calculate_checksums(path, chunk_size):
        """
        Returns the the file's MD5 and its individual CRC chunk values

        @type path: str
        @type chunk_size: int
        @rtype: tuple
        """
        checksums = []
        md5 = hashlib.md5()

        with open(path, 'rb') as f:
            chunk = f.read(chunk_size)

            while chunk:
                checksums.append(binascii.crc32(chunk) & 0xffffffff)
                md5.update(chunk)
                chunk = f.read(chunk_size)

        # In the case of a zero-byte file, just return zero
        if len(checksums) == 0:
            checksums.append(0)
            md5.update('')

        return md5.hexdigest(), checksums
