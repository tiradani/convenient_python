# Python Packages

I found that I keep looking up code for the same tasks over and over.  I decided to simplify my life and create
convenience packages for all the code that I re-use and re-lookup continually.

Where noted, some modules have been copied and possibly modify from other locations.  The license under which these
modules are distributed have been noted as well as the location of the original source.

## arg_handler
Provides a helper module for parsing command line options and arguments.

## ini_handler
Provides a helper module for ini files.  It wraps the reading and retrieving of values from ini files into a single class.

## multi_logging
Provides a helper module for logging.  There is a single unified class that sets up logging.  The class can be multiple times.  Each instance can set up one of the following types of logs:

CONSOLE:
: prints all statements to either stdout or stderr depending on the log level

FILE:
: uses the python logging module to log to specified files

SYSLOG:
: logs output to syslog

## os_utils
Provides python implementations of many shell commands.  This module also includes several sub-modules.

### os_utils.daemonize
This module is distributed under the MIT license.

Original source: <https://github.com/thesharp/daemonize>

### os_utils.ipaddr
This module is licensed under the Apache License, Version 2.0 (the "License")

Original source: <https://code.google.com/p/ipaddr-py/>

### os_utils.openssh_wrapper
AUTHORS:
* Roman Imankulov <roman@netangels.ru>
* Jan-Oliver Kaiser <mail@janno-kaiser.de>
* Pavel Vavilin <shtartora@gmail.com>

cloned from:  <https://github.com/NetAngels/openssh-wrapper.git>

## py_utils
Provides useful utility functions for python programming tasks.

## python_fstab
Provides python-fstab module for reading and editing fstab files in python.  The package was apparently 
written for and subsequently removed from Ubuntu/Debian.  The source has been modified to include more properties.  
The original source for this package can be found at:

<https://github.com/ProteinSimple/python-fstab>

This module is distributed under the GNU General Public License (version 3).

## xml
Provides a common interface for parsing xml and performing xsl transforms in python

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
cd <path/to>/py_stdlib
./build.sh
```

Source RPMs will b located in:

```bash
/path/to/convenient-python/rpmbuild/SRPMS
```

The built RPMs will be in:

```bash
/path/to/convenient-python/rpmbuild/RPMS
```
