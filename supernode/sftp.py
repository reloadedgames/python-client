from paramiko import SFTPClient
import binascii
import errno
import os
import paramiko
import StringIO


class UploadClient(SFTPClient):
    def __init__(self, settings):
        """
        Initializes a new connected UploadClient

        @param settings: The SFTP settings
        @type settings: dict
        """

        # Initialize SSH client
        self.settings = settings
        self.ssh = self.ssh_client()

        # Copy functionality from the static from_transport() method
        chan = self.ssh.get_transport().open_session()

        if chan is None:
            raise Exception('Failure connecting to SFTP server')

        chan.invoke_subsystem('sftp')
        super(UploadClient, self).__init__(chan)

    def ssh_client(self):
        """
        Connects to the SFTP server using the supplied settings and returns an SFTPClient

        @rtype : SSHClient
        """
        # Load the private key from a string
        key_file = StringIO.StringIO(self.settings['private_key'])
        #noinspection PyTypeChecker
        key = paramiko.DSSKey.from_private_key(key_file)

        # Open a connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(hostname=self.settings['host'], port=self.settings['port'],
                        username=self.settings['username'], pkey=key, look_for_keys=False)

        except paramiko.AuthenticationException:
            exit('Failure authenticating with server')

        # Older paramiko packages don't support setting this in connect(), so set it here instead
        ssh.get_transport().use_compression(True)

        # Verify fingerprint
        fingerprint = self.settings['fingerprint'].replace(':', '')
        server_key = ssh.get_transport().get_remote_server_key()
        server_fingerprint = binascii.hexlify(server_key.get_fingerprint())

        if server_fingerprint != fingerprint:
            print 'The fingerprint supplied by the host does not match:'
            print '  Client: {0}'.format(fingerprint)
            print '  Host: {0}'.format(server_fingerprint)
            exit(1)

        return ssh

    def path_exists(self, path):
        """
        Returns whether the specified path exists on the remote server

        @param path: The remote server path
        @type path: str
        @rtype : bool
        """
        try:
            self.stat(path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False

            raise

        return True

    def upload_file(self, file_path, server_path, callback):
        """
        Manually performs the file upload with skip and resume support

        @param file_path: The local file path
        @type file_path: str
        @param server_path: The remote file path
        @type server_path: str
        @param callback: The callback function to execute while performing the upload
        @type callback: function(str, int, int)
        """
        file_size = os.path.getsize(file_path)
        server_size = 0

        if self.path_exists(server_path):
            server_size = self.stat(server_path).st_size

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
            server_file = self.open(server_path, mode)

            try:
                server_file.set_pipelined(True)
                server_file.seek(offset)
                data = local_file.read(byte_size)

                while data:
                    server_file.write(data)
                    server_size += len(data)
                    callback(server_path, server_size, file_size)

                    data = local_file.read(byte_size)
            finally:
                server_file.close()