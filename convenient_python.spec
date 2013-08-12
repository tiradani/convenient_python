%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           convenient_python
Group:          System Environment/Libraries
Version:        0
Release:        1%{?dist}
Summary:        Provides many helper modules for common uses cases when programming with Python (2.6+)

License:        Fermitools Software Legal Information (Modified BSD License)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       convenient_python = %{version}-%{release}

Source:         convenient_python.tar.gz


%description
Provides the following modules:

convenient_python.arg_handler
    Provides a helper module for parsing command line options and arguments.

convenient_python.ini_handler
    Provides a helper module for ini files.  It wraps the reading and retrieving
    of values from ini files into a single class.

convenient_python.logging
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

convenient_python.os_utils
    Provides python implementations of many shell commands.

convenient_python.py_utils
    Provides useful utility functions for python programming tasks.

convenient_python.python_fstab
    Provides python-fstab module for reading and editing fstab files in python.
    The package was apparently written for and subsequently removed from 
    Ubuntu/Debian.  The source has been modified to include more properties.  
    The original source for this package can be found at:

        <https://github.com/ProteinSimple/python-fstab>

convenient_python.xml
    Provides a common interface for parsing xml and performing xsl transforms 
    in python


%prep
%setup -q -n convenient_python

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r ../convenient_python $RPM_BUILD_ROOT%{python_sitelib}

%files
%{python_sitelib}/convenient_python/

%changelog
* Mon May 10 2013 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.1
- initial packaging


