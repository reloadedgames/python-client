"""
Uploads the package contents. All arguments are optional as they will be
queried from the REST API when the command is executed.

Usage:
    upload.py [options]
    upload.py -h | --help

Options:
    --fingerprint <fingerprint>     The fingerprint of the host
    --host <host>                   The host name
    --key <path>                    The private key path
    --port <port>                   The host port
    --username <username>           The username
"""

from supernode.command import Command
from supernode.sftp import UploadClient
import os
import sys


class UploadCommand(Command):
    def help(self):
        return __doc__

    def run(self, options):
        # Validate settings
        if ('partner_id', 'version_id', 'path') <= self.settings.keys():
            exit('The current saved configuration does not support uploading')

        print 'Querying upload settings...'
        settings = self.api.get_upload_settings(self.settings['partner_id'])
        settings = self.merge_options(options, settings)

        print 'Connecting to server...'
        sftp = UploadClient(settings)

        print 'Uploading files...'
        package_id = self.settings['package_id']
        version_id = self.settings['version_id']
        path = self.settings['path']

        # Create package/version folders
        if not sftp.path_exists(package_id):
            sftp.mkdir(package_id)

        sftp.chdir(package_id)

        if not sftp.path_exists(version_id):
            sftp.mkdir(version_id)

        sftp.chdir(version_id)

        for root, dirs, files in os.walk(path):
            for d in dirs:
                server_path = os.path.join(root, d).replace(path, '').replace('\\', '/').lstrip('/\\')

                if not sftp.path_exists(server_path):
                    sftp.mkdir(server_path)

            for f in files:
                file_path = os.path.join(root, f)
                server_path = file_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                sftp.upload_file(file_path, server_path, self.upload_progress)

        sftp.close()

    @staticmethod
    def merge_options(options, settings):
        """
        Merges the command-line options and REST API settings into a single dictionary

        @param options: The incoming command-line options
        @type options: dict
        @param settings: The settings from the API
        @type settings: dict
        @rtype : dict
        """
        host = options['--host']
        port = options['--port']
        username = options['--username']
        key_path = options['--key']
        fingerprint = options['--fingerprint']

        if host is not None:
            settings['host'] = host

        if port is not None and port.isdigit():
            settings['port'] = int(port)

        if username is not None:
            settings['username'] = username

        if key_path is not None and os.path.isfile(key_path):
            with open(key_path, 'r') as f:
                settings['private_key'] = f.read()

        if fingerprint is not None:
            settings['fingerprint'] = fingerprint

        return settings

    @staticmethod
    def upload_progress(path, size, file_size):
        """
        Updates the progress of the file transfer

        @param path: The path of the file
        @type path: str
        @param size: The bytes transferred
        @type size: int
        @param file_size: The total file size
        @type file_size: int
        """

        # Truncate the path to avoid spilling onto two lines
        max_length = 65

        if len(path) > max_length:
            path = '...' + path[-max_length:]

        # Keep refreshing the same line until complete
        percent = float(size) / file_size * 100
        print '\r  {0} - {1:.0f}%'.format(path, percent),
        sys.stdout.flush()

        if size >= file_size:
            print ''