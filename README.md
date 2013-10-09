# Python Package Manager

This project contains Python scripts for command-line package management.

## Python Version

- 2.7 on Windows 7 x64 (development environment)

## Required Packages

All of the required packages can be installed through pip:

- [docopt](https://github.com/docopt/docopt)
- [paramiko](https://github.com/paramiko/paramiko)
- [requests](http://docs.python-requests.org/en/latest/)

### Windows

The paramiko package will fail to install on Windows because of its dependency on PyCrypto (a C library). You can download and install a pre-built version for your specific Python/Windows version using the link below:

- [Voicespace Python Modules](http://www.voidspace.org.uk/python/modules.shtml#pycrypto)

## Scripts Overview

The command-line tool includes the following scripts:

|Script|Purpose|
|:-----|:-------|
|complete.py|Sets the newly created version as the current package version.|
|config.py|Collects and stores the configuration information needed to use other commands.|
|create.py|Creates a new package.|
|update.py|Updates an existing package with a new version.|
|upload.py|Uploads package contents to the SFTP infrastructure.|

### Script Arguments and Help

Each script has a different set of arguments. For help with a script, execute the script passing the `-h` option:

```
python config.py -h

Collects and stores the configuration information needed to use other commands.

Usage:
    config.py [options]
    config.py -h | --help

Options:
    --email <email>             The user e-mail address
    --password <password>       The user password
    --partnerid <partnerid>     The partner ID
    --url <url>                 The REST API URL

If passed all options, the configuration will be validated and saved.
Otherwise, you will be prompted for the missing configuration information.

Configurations are stored in your home folder under the file: ~/.package.config
```

