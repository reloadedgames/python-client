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
import binascii
import os
import paramiko
import requests
import StringIO


class UploadCommand:
    def __init__(self):
        self._settings = ConfigCommand.load()

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
        settings = self.get_upload_settings()
        settings = self.merge_options(options, settings)

        print 'Connecting to server...'
        ssh = self.ssh_client(settings)
        sftp = ssh.open_sftp()
        contents = sftp.listdir_attr('.')

        for item in contents:
            print item

        ssh.close()

    def get_upload_settings(self):
        """
        Pulls the upload settings from the REST API

        @rtype : dict
        """
        settings = self._settings
        url = '{0}/settings/upload'.format(settings['url'])

        response = requests.get(url)

        if response.status_code != 200:
            exit('There was a problem querying the upload settings')

        json = response.json()

        return {
            'host': json['Host'],
            'port': int(json['Port']),
            'fingerprint': json['Fingerprints']['DSA'],
            'username': settings['partner_id'],
            'private_key': self.get_private_key()
        }

    def get_private_key(self):
        """
        Queries the private key from the REST API

        @rtype string
        """
        settings = self._settings
        url = '{0}/partners/{1}/private-key'.format(settings['url'], settings['partner_id'])
        credentials = (settings['email'], settings['password'])

        response = requests.get(url, auth=credentials)

        if response.status_code != 200:
            exit('There was a problem querying the private key')

        return response.content

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

# Handles script execution
if __name__ == '__main__':
    args = docopt(__doc__)
    command = UploadCommand()
    command.run(args)