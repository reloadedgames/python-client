import ConfigParser
import os


class Config:
    """
    Handles passing around configuration settings and loads/saves them to disk
    """
    def __init__(self):
        # Globally required
        self.email = None
        self.password = None
        self.url = None
        self.partner_id = None

        # Checkum
        self.package_path = None

        # Package and versions
        self.package_id = None
        self.version_id = None

        self._path = os.path.expanduser('~/.package')
        self._config = ConfigParser.ConfigParser(allow_no_value=True)

        try:
            self.load()
        except ConfigParser.NoSectionError as e:
            self.save()

    def load(self):
        """
        Loads the configuration from disk
        """
        self._config.read(self._path)

        self.email = self._config.get('general', 'email')
        self.password = self._config.get('general', 'password')
        self.url = self._config.get('general', 'url')
        self.partner_id = self._config.get('general', 'partner_id')

        self.package_path = self._config.get('package', 'package_path')
        self.package_id = self._config.get('package', 'package_id')
        self.version_id = self._config.get('package', 'version_id')

    def save(self):
        """
        Saves the configuration to disk
        """
        if not self._config.has_section('general'):
            self._config.add_section('general')

        if not self._config.has_section('package'):
            self._config.add_section('package')

        self._config.set('general', 'email', self.email)
        self._config.set('general', 'password', self.password)
        self._config.set('general', 'url', self.url)
        self._config.set('general', 'partner_id', self.partner_id)

        self._config.set('package', 'package_path', self.package_path)
        self._config.set('package', 'package_id', self.package_id)
        self._config.set('package', 'version_id', self.version_id)

        with open(self._path, 'wb') as f:
            self._config.write(f)