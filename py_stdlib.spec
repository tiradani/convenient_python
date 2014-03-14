%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           py_stdlib
Group:          System Environment/Libraries
Version:        0
Release:        2%{?dist}
Summary:        Provides many helper modules for common uses cases when programming with Python (2.6+)

License:        Fermitools Software Legal Information (Modified BSD License)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       py_stdlib = %{version}-%{release}

Source:         py_stdlib-%{version}.tar.gz


%description
Provides the following modules:

py_stdlib.arg_handler
    Provides a helper module for parsing command line options and arguments.

py_stdlib.ini_handler
    Provides a helper module for ini files.  It wraps the reading and retrieving
    of values from ini files into a single class.

py_stdlib.logging
    Provides a helper module for logging.  There is a single unified class that
    sets up logging.  The class can be multiple times.  Each instance can set up
    one of the following types of logs:

        CONSOLE:
            prints all statements to either stdout or stderr depending on the 
            log level

        FILE:
            uses the python logging module to log to specified files

        SYSLOG:
            logs output to syslog

py_stdlib.os_utils
    Provides python implementations of many shell commands.

py_stdlib.py_utils
    Provides useful utility functions for python programming tasks.

py_stdlib.python_fstab
    Provides python-fstab module for reading and editing fstab files in python.
    The package was apparently written for and subsequently removed from 
    Ubuntu/Debian.  The source has been modified to include more properties.  
    The original source for this package can be found at:

        <https://github.com/ProteinSimple/python-fstab>

py_stdlib.xml
    Provides a common interface for parsing xml and performing xsl transforms 
    in python


%prep
%setup -q -n py_stdlib-%{version}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r py_stdlib $RPM_BUILD_ROOT%{python_sitelib}

%files
%{python_sitelib}/py_stdlib/

%changelog
* Fri Mar 14 2014 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.2
- fixed a syslog bug
- added timed command

* Mon May 10 2013 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.1
- initial packaging


