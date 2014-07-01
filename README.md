# Python Package Manager

This project provides command-line tools for creating and managing super node packages. 

Python versions 2.6 and 2.7 are supported.

**Installation**

* [Compatibility Testing](#compatibility-testing)
* [Linux Installation](#linux-installation)
* [Windows Installation](#windows-installation)

**Usage**

* [Commands Overview](#commands-overview)
* [Creating a Package](#creating-a-package)
* [Updating a Package](#updating-a-package)


## Compatibility Testing

|Status|Operating System|Python Version(s)|Notes|
|:----:|:---------------|:----------------|:----|
|:white_check_mark:|Amazon Linux AMI 2013.09|2.6.8||
|:white_check_mark:|CentOS 6 - 2013-05-27|2.6.6||
|:white_check_mark:|Red Hat Enterprise Linux 6.4|2.6.6||
|:white_check_mark:|SUSE Linux Enterprise Server 11 SP3|2.6.8|Use the `config --insecure` option to disable HTTPS verification.|
|:white_check_mark:|Ubuntu Server 12.04.2 LTS|2.7.3||
|:white_check_mark:|Ubuntu Server 13.04|2.6.8, 2.7.4||
|:white_check_mark:|Windows 7|2.6.6, 2.7.5||

## Linux Installation

Some operating system packages are required to compile the [PyCrypto](https://pypi.python.org/pypi/pycrypto)
C library. Other packages (such as git and pip) aren't required but are used to ease installation.

Depending on your distribution, execute the appropriate command(s):

|Distribution|Command|
|:-----------|:-------|
|Amazon AMI|`yum install -y gcc git python2-devel python-setuptools python-pip`|
|CentOS|`yum install -y gcc git python2-devel python-setuptools`<br>`easy_install pip`|
|Debian, Ubuntu|`apt-get install -y gcc git python-dev python-pip`|
|OpenSUSE|`zypper in -y gcc git python-devel python-setuptools`<br>`easy_install pip`|
|Red Hat|`yum erase -y python-paramiko python-crypto`<br>`yum install -y gcc git python2-devel python-setuptools`<br>`easy_install pip`|

After installing the required packages, clone the client's repository using [git](http://git-scm.com/):

```bash
$ git clone https://github.com/reloadedgames/python-client.git
```

After cloning has finished, install the program using [pip](http://www.pip-installer.org/):

```bash
$ pip install ./python-client
```

Once installed, the client will automatically be added to your path and can be run using the `supernode` command.

## Windows Installation

Download and install the latest Python 2.7 for Windows release:

- [Download Python](http://www.python.org/getit/)

Download and install the setuptools and pip modules:

- [Setuptools](http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools)
- [Pip](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)

Add both the Python root installation folder (`C:\Python27\`) and its scripts folder (`C:\Python27\Scripts\`)
to your environment path variable. This will allow you to access the python and pip commands easily.

Download and install the pre-built version of the [PyCrypto](https://pypi.python.org/pypi/pycrypto)
library for your specific Python/Windows environment:

- [Voicespace Python Modules](http://www.voidspace.org.uk/python/modules.shtml#pycrypto)

Assuming you have [git](http://git-scm.com/) installed, clone the client repository:

```bat
C:\> git clone https://github.com/reloadedgames/python-client.git
```

Once cloned, install the client using [pip](http://www.pip-installer.org/):

```bat
C:\> pip install ./python-client
```

Once installed, the client will automatically be added to your path and can be run using the `supernode` command.

## Commands Overview

The command-line tool provides multiple commands used to create and manage packages. You can view the help for each
command by using the `-h` or `--help` argument:

```bash
$ supernode -h
Provides commands for creating and managing super node packages.

Usage:
    supernode <command> [<args>...]
    supernode <command> -h | --help
    supernode -h | --help

Commands:
    config      Collects configuration information needed to use other commands
    create      Creates a new package
    tag         Updates the specified version tag for a package
    update      Updates an existing package with a new version
    upload      Uploads the package contents to the S3 origin bucket
```

Each command will also provide its own help:

```bash
$ supernode config -h
Collects and stores the configuration information needed to use other commands.

Usage:
    supernode config [options]
    supernode config -h | --help

Options:
    --email <email>             The user e-mail address
    --insecure                  Disables HTTPS certificate validation
    --password <password>       The user password
    --partnerid <partnerid>     The partner ID
    --url <url>                 The REST API URL
                                    [default: https://manifests.reloadedtech.com]

If passed all options, the configuration will be validated and saved.
Otherwise, you will be prompted for the missing configuration information.

Configurations are stored in your home folder under the file: ~/.package.config
```

## Creating a Package

To create a new package, you must first configure the package environment. The `supernode config` command will prompt you
for any missing configuration information that is not supplied as an argument.

```bash
$ supernode config
E-mail: user@example.com
Password: ******
Validating credentials...
Multiple partners were found. Please select one from the following:

1. GamersFirst
2. K2 Network
3. Reloaded Games
4. Reloaded Technologies

Please enter the number of the partner: 1
Saving configuration...
```

The package environment settings are stored in your home directory and are used when executing other commands.

After configuring your environment, you create the package:

```bash
$ supernode create --path /tmp/packages/example \
  --run /tmp/packages/example/Installer.exe \
  --name "Python Client Test Package"
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

Now that the package has been created, its files must be uploaded to the S3 origin bucket:

```bash
$ supernode upload
Querying upload credentials...
Connecting to S3 bucket...
Querying existing objects...
Querying multipart uploads...
Uploading files...
100% Installer.bin                                    637.62 kB/s Time: 0:14:01
100% Installer.exe                                     23.65 kB/s Time: 0:00:00
Upload complete.
```

Once the package files have been uploaded, you can then set the current version tag of the package:

```bash
$ supernode tag --tag current
Setting package tag...
```

## Updating a Package

Updating an existing package with a new version is similar to creating a new package. 
You follow the same previous steps:

- Configure the environment (optional)
- Update the package
- Upload the files
- Set the current package tag

Updating a package takes almost the same arguments as creating a package:

```bash
$ supernode update --path /tmp/packages/example2 \
  --run /tmp/packages/example2/Installer.exe
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
