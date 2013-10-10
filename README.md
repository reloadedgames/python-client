# Python Package Manager

This project contains Python scripts for command-line package management.

## Compatibility Testing

|Status|Operating System|Python Version|Notes|
|:----:|:---------------|:-------------|:----|
|:white_check_mark:|Ubuntu 13.04 x64|2.7.4||
|:white_check_mark:|Windows 7 x64|2.6.6||
|:white_check_mark:|Windows 7 x64|2.7.5|Development environment|
|:red_circle:|Windows 7 x64|3.0.1|Broken due to setuptools|
|:red_circle:|Windows 7 x64|3.1.4|Broken due to docopt|

## Required Packages

All of the required packages can be installed through pip:

- [docopt v0.6.1](https://github.com/docopt/docopt)
- [paramiko](https://github.com/paramiko/paramiko)
- [requests](http://docs.python-requests.org/en/latest/)

### Docopt

Install the specific version of docopt using the following command:

```
$ pip install docopt==0.6.1
```

### Windows

The paramiko package will fail to install on Windows because of its dependency on PyCrypto (a C library). 
You can download and install a pre-built version for your specific Python/Windows version using the link below:

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

Each script has a different set of arguments. For help with a script, execute the script using the `-h` option:

```
$ python config.py -h

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

## Creating a Package

To create a new package, you must first configure the package environment:

```
$ python config.py --email=user@example.com --password=password
  --url=https://manifests.sandbox.reloadedtech.com

Validating credentials...
Multiple partners were found. Please select one from the following:

0. GamersFirst
1. K2 Network
2. Reloaded Games
3. Reloaded Technologies

Please enter the number of the partner: 0
Saving configuration...
```

The package environment settings are stored in your home directory and are used when executing other commands.

After configuring your environment, you create the package:

```
$ python create.py --path "C:\Packages\Example" --run "C:\Packages\Example\Installer.exe"
  --name "Python Client Test Package" --arguments "/install /quiet" --version-name "Version 1.00"

Creating new package...
Processing package files...
Creating new version...
Adding files to version...
  Installer.bin
  Installer.exe
Marking the version as complete...
Saving package information to configuration...
Package complete.

PackageId = 5255da8e35edd10a8809c8de
VersionId = 5255da8e35edd10a8809c8df
```

The package and version information is automatically saved in your configuration after executing the command.

Now that the package has been created, its files must be uploaded to the SFTP infrastructure:

```
$ python upload.py

Querying upload settings...
Connecting to server...
Uploading files...
  Installer.bin - 100%
  Installer.exe - 100%
```

Once the package files have been uploaded, you can then set the current version of the package:

```
$ python complete.py

Updating the current package version to 5255da8e35edd10a8809c8df...
```

## Updating a Package

Updating an existing package with a new version is similar to creating a new package. 
You follow the same previous steps:

- Configure the environment (optional)
- Update the package
- Upload the files
- Set the current package version

Updating a package takes almost the same arguments as creating a package:

```
$ python update.py --path "C:\Packages\Example2" --run "C:\Packages\Example2\Installer.exe" 
  --arguments "/install /quiet" --version-name "Version 2.00"

Processing package files...
Creating new version...
Adding files to version...
  Installer.bin
  Installer.exe
Marking the version as complete...
Saving package information to configuration...
Package complete.

PackageId = 5255da8e35edd10a8809c8de
VersionId = 5255de8335edd10a8809c8e2
```

