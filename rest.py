import requests


class RestApi:
    def __init__(self, url, email, password):
        """
        Initializes the RestApi class

        @param url: The base URL of the REST API
        @type url: str
        @param email: The user's e-mail address
        @type email: str
        @param password: The user's password
        @type password: str
        """
        self.url = url
        self.email = email
        self.password = password

    def auth(self):
        """
        Returns a tuple used for authenticating an API request

        @rtype : tuple
        """
        return self.email, self.password

    def get_user_partners(self):
        """
        Returns all of the partners which the user may access

        @rtype : list
        """
        response = requests.get('{0}/users/current/partners'.format(self.url), auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure querying user partners')

        return response.json()

    def create_package(self, partner_id, name, package_type):
        """
        Creates the package through the REST API and returns its information

        @param partner_id: The partner primary key
        @type partner_id: str
        @param name: The package name
        @type name: str
        @param package_type: The package type
        @type package_type: str
        @rtype : dict
        """
        url = '{0}/packages'.format(self.url)
        parameters = {
            'Name': name,
            'PartnerId': partner_id,
            'Type': package_type
        }

        response = requests.post(url, parameters, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure creating package')

        return response.json()

    def create_version(self, package_id, run, arguments=None, name=None):
        """
        Creates the package version and returns its information

        @param package_id: The primary key of the package
        @type package_id: str
        @param run: The file to run
        @type run: str
        @param arguments: The run file arguments
        @type arguments: str
        @param name: The name of the version
        @type name: str
        @rtype : dict
        """
        url = '{0}/packages/{1}/versions'.format(self.url, package_id)
        parameters = {
            'Arguments': arguments,
            'Name': name,
            'Run': run
        }

        response = requests.post(url, parameters, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure creating version')

        return response.json()

    def add_file(self, version_id, path, size, chunk_size, checksums):
        """
        Adds the file to the package version

        @param version_id: The primary key of the version
        @type version_id: str
        @param path: The relative path to the file
        @type path: str
        @param size: The size of the file
        @type size: long
        @param chunk_size: The size of each file chunk
        @type chunk_size: long
        @param checksums: A list of checksum values
        @type checksums: list

        """
        url = '{0}/versions/{1}/files'.format(self.url, version_id)
        parameters = {
            'Checksums': ','.join(str(i) for i in checksums),
            'Chunk': chunk_size,
            'Path': path,
            'Size': size
        }

        response = requests.post(url, parameters, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure adding file')

    def complete_version(self, version_id):
        """
        Marks the version as complete after all of the files have been added

        @param version_id: The primary key of the version
        @type version_id: str
        """
        url = '{0}/versions/{1}/complete'.format(self.url, version_id)
        response = requests.post(url, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure completing version')

    def get_upload_settings(self, partner_id):
        """
        Pulls the upload settings from the REST API

        @param partner_id: The primary key of the partner
        @type partner_id: str
        @rtype : dict
        """
        response = requests.get('{0}/settings/upload'.format(self.url))

        if response.status_code != 200:
            raise Exception('Failure querying upload settings')

        json = response.json()

        return {
            'host': json['Host'],
            'port': int(json['Port']),
            'fingerprint': json['Fingerprints']['DSA'],
            'username': partner_id,
            'private_key': self.get_private_key(partner_id)
        }

    def get_private_key(self, partner_id):
        """
        Queries the private key for the partner from the REST API

        @param partner_id: The primary key of the partner
        @type partner_id: str
        @rtype : str
        """
        url = '{0}/partners/{1}/private-key'.format(self.url, partner_id)
        response = requests.get(url, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure querying private key')

        return response.content

    def set_version(self, package_id, version_id):
        """
        Sends the API request updating the package version

        @param package_id: The primary key of the package
        @type package_id: str
        @param version_id: The primary key of the version
        @type version_id: string
        """
        url = '{0}/packages/{1}'.format(self.url, package_id)
        parameters = {
            'VersionId': version_id
        }

        response = requests.put(url, parameters, auth=self.auth())

        if response.status_code != 200:
            raise Exception('Failure setting package version')