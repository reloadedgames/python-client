import requests


class RestApi:
    def __init__(self, settings):
        """
        Initializes the RestApi class

        @param settings: The API settings
        @type settings: dict
        """
        self.url = settings['url']
        self.email = settings['email']
        self.password = settings['password']
        self.verify = settings['verify'] == 'True'

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
        response = requests.get('{0}/users/current/partners'.format(self.url), auth=self.auth(), verify=self.verify)

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

        response = requests.post(url, parameters, auth=self.auth(), verify=self.verify)

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

        # Manually set the content-length header value if all parameter values are None
        # This is a workaround for this annoying bug: https://github.com/kennethreitz/requests/issues/223
        headers = {
            'Content-Length': '0'
        }

        for key in parameters:
            if parameters[key] is not None:
                headers = None

        response = requests.post(url, parameters, headers=headers, auth=self.auth(), verify=self.verify)

        if response.status_code != 200:
            raise Exception('Failure creating version')

        return response.json()

    def add_file(self, version_id, path, size, chunk_size, checksums, md5):
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
        @param md5: The MD5 hex of the file
        @type md5: str
        @type checksums: list

        """
        url = '{0}/versions/{1}/files'.format(self.url, version_id)
        parameters = {
            'Checksums': ','.join(str(i) for i in checksums),
            'Chunk': chunk_size,
            'MD5': md5,
            'Path': path,
            'Size': size
        }

        response = requests.post(url, parameters, auth=self.auth(), verify=self.verify)

        if response.status_code != 200:
            raise Exception('Failure adding file')

    def complete_upload(self, version_id):
        """
        Marks the version as completely uploaded

        @type version_id str
        """
        url = '{0}/versions/{1}/upload-complete'.format(self.url, version_id)
        response = requests.post(url, auth=self.auth(), verify=self.verify)

        if response.status_code != 200:
            raise Exception('Failure completing version')

    def get_upload_credentials(self, version_id):
        """
        Returns the upload credentials for the version

        @type version_id str
        @rtype: dict
        """

        url = '{0}/versions/{1}/upload-credentials'.format(self.url, version_id)
        response = requests.get(url, auth=self.auth(), verify=self.verify)

        if response.status_code != 200:
            raise Exception('Failure querying upload credentials')

        return response.json()

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

        response = requests.put(url, parameters, auth=self.auth(), verify=self.verify)

        if response.status_code != 200:
            raise Exception('Failure setting package version')
