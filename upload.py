"""
Uploads the package contents. All arguments are optional as they will be
queried from the REST API when the command is executed.

Usage:
    upload.py [options]
    upload.py -h | --help

Options:
    --host <host>                   The host name
    --port <port>                   The host port
    --username <username>           The username
    --key <path>                    The private key path
    --fingerprint <fingerprint>     The fingerprint of the host
"""

from config import ConfigCommand
from docopt import docopt
from rest import RestApi
import binascii
import errno
import os
import paramiko
import StringIO


class UploadCommand:
    def __init__(self):
        self._settings = ConfigCommand.load()
        self.rest = RestApi(self._settings['url'], self._settings['email'], self._settings['password'])
        self._upload_file = None
        self._upload_percent = None

        # Validate settings
        if ('partner_id', 'version_id', 'path') <= self._settings.keys():
            exit('The current saved configuration does not support uploading')

    def run(self, options):
        """
        Executes the command

        @param options: The incoming command-line options
        @type options: dict
        """
        print 'Querying upload settings...'
        settings = self.rest.get_upload_settings(self._settings['partner_id'])
        settings = self.merge_options(options, settings)

        print 'Connecting to server...'
        ssh = self.ssh_client(settings)
        sftp = ssh.open_sftp()

        print 'Uploading files...'
        package_id = self._settings['package_id']
        version_id = self._settings['version_id']
        path = self._settings['path']

        # Create package/version folders
        if not self.path_exists(sftp, package_id):
            sftp.mkdir(package_id)

        sftp.chdir(package_id)

        if not self.path_exists(sftp, version_id):
            sftp.mkdir(version_id)

        sftp.chdir(version_id)

        # Recursively upload files
        for root, dirs, files in os.walk(path):
            for d in dirs:
                server_path = os.path.join(root, d).replace(path, '').replace('\\', '/').lstrip('/\\')

                if not self.path_exists(sftp, server_path):
                    sftp.mkdir(server_path)

            for f in files:
                file_path = os.path.join(root, f)
                server_path = file_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                self._upload_file = server_path
                self._upload_percent = 0

                sftp.put(file_path, server_path, callback=self.upload_progress)

        sftp.close()
        ssh.close()

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
    def ssh_client(settings):
        """
        Connects to the SFTP server using the supplied settings and returns an SFTPClient

        @param settings: The upload settings
        @type settings: dict
        @rtype : SSHClient
        """
        # Load the private key from a string
        key_file = StringIO.StringIO(settings['private_key'])
        key = paramiko.DSSKey.from_private_key(key_file)

        # Open a connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(hostname=settings['host'], port=settings['port'],
                        username=settings['username'], pkey=key, look_for_keys=False,
                        compress=True)

        except paramiko.AuthenticationException:
            exit('Failure authenticating with server')

        # Verify fingerprint
        fingerprint = settings['fingerprint'].replace(':', '')
        server_key = ssh.get_transport().get_remote_server_key()
        server_fingerprint = binascii.hexlify(server_key.get_fingerprint())

        if server_fingerprint != fingerprint:
            print 'The fingerprint supplied by the host does not match:'
            print '  Client: {0}'.format(fingerprint)
            print '  Host: {0}'.format(server_fingerprint)
            exit(1)

        return ssh

    @staticmethod
    def path_exists(sftp, path):
        """
        Returns whether the specified path exists on the remote server

        @param sftp: The SFTPClient object
        @type sftp: SFTPClient
        @param path: The remote server path
        @type path: str
        @rtype : bool
        """
        try:
            sftp.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False

            raise

        return True

    def upload_progress(self, size, file_size):
        """
        Updates the progress of the file transfer

        @param size: The bytes transferred
        @type size: int
        @param file_size: The total file size
        @type file_size: int
        """
        if self._upload_percent == 100:
            print ''
            return

        # Keep refreshing the same line until complete
        self._upload_percent = float(size) / file_size * 100
        print '\r  {0} - {1:.0f}%'.format(self._upload_file, self._upload_percent),

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = UploadCommand()
    command.run(args)