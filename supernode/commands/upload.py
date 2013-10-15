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
import binascii
import errno
import os
import paramiko
import StringIO
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
        ssh = self.ssh_client(settings)
        sftp = ssh.open_sftp()

        print 'Uploading files...'
        package_id = self.settings['package_id']
        version_id = self.settings['version_id']
        path = self.settings['path']

        # Create package/version folders
        if not self.path_exists(sftp, package_id):
            sftp.mkdir(package_id)

        sftp.chdir(package_id)

        if not self.path_exists(sftp, version_id):
            sftp.mkdir(version_id)

        sftp.chdir(version_id)

        for root, dirs, files in os.walk(path):
            for d in dirs:
                server_path = os.path.join(root, d).replace(path, '').replace('\\', '/').lstrip('/\\')

                if not self.path_exists(sftp, server_path):
                    sftp.mkdir(server_path)

            for f in files:
                file_path = os.path.join(root, f)
                server_path = file_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                self.upload_file(sftp, file_path, server_path)

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
                        username=settings['username'], pkey=key, look_for_keys=False)

        except paramiko.AuthenticationException:
            exit('Failure authenticating with server')

        # Older paramiko packages don't support setting this in connect(), so set it here instead
        ssh.get_transport().use_compression(True)

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

    def upload_file(self, sftp, file_path, server_path):
        """
        Manually performs the file upload with skip and resume support

        @param sftp: The SFTPClient connection
        @type sftp: SFTPClient
        @param file_path: The local file path
        @type file_path: str
        @param server_path: The remote file path
        @type server_path: str
        """
        file_size = os.path.getsize(file_path)
        server_size = 0

        if self.path_exists(sftp, server_path):
            server_size = sftp.stat(server_path).st_size

        # Skip completed files
        if file_size == server_size:
            return

        # Clean upload
        mode = 'w'
        offset = 0
        byte_size = 32768

        # Resume
        if server_size > 0:
            mode = 'r+'
            offset = server_size - 1

        with open(file_path, 'rb') as local_file:
            local_file.seek(offset)
            server_file = sftp.open(server_path, mode)

            try:
                server_file.set_pipelined(True)
                server_file.seek(offset)
                data = local_file.read(byte_size)

                while data:
                    server_file.write(data)
                    server_size += len(data)
                    self.upload_progress(server_path, server_size, file_size)

                    data = local_file.read(byte_size)
            finally:
                server_file.close()

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