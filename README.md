# Python Packages


## cms_argument_handler
Provides a helper module for parsing command line options and arguments.

## cms_ini_handler
Provides a helper module for ini files.  It wraps the reading and retrieving of values from ini files into a single class.

## cms_logging
Provides a helper module for logging.  There is a single unified class that sets up logging.  The class can be multiple times.  Each instance can set up one of the following types of logs:

CONSOLE:
: prints all statements to either stdout or stderr depending on the log level

FILE:
: uses the python logging module to log to specified files

SYSLOG:
: logs output to syslog

## cms_os_utils
Provides python implementations of many shell commands.

## python_fstab
Provides python-fstab module for reading and editing fstab files in python.  The package was apparently written for and subsequently removed from Ubuntu/Debian.  The source has been modified to include more properties.  The original source for this package can be found at:

<https://github.com/ProteinSimple/python-fstab>

# Building RPMs with Mock

## Install Mock
On Fedora systems:
```bash
yum install mock
```

On SL6 systems:
```bash
rpm -Uvh http://mirrors.nebo.edu/public/epel/6/i386/epel-release-6-8.noarch.rpm
yum install mock
```

## Build RPMs
Execute the following:

```bash
cd <path/to>/cms-python-modules
./build.sh
```

Source RPMs will b located in:

```bash
/home/tiradani/workspace/cms-python-modules/rpmbuild/SRPMS
```

The built RPMs will be in:

```bash
/home/tiradani/workspace/cms-python-modules/rpmbuild/RPMS
```
