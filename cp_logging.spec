%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           cp_logging
Group:          System Environment/Libraries
Version:        0
Release:        1%{?dist}
Summary:        Helper module for logging.

License:        Fermitools Software Legal Information (Modified BSD License)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       cp_logging = %{version}-%{release}

Source:         cp_logging.tar.gz


%description
Provides a helper module for logging.  There is a single unified class that sets
up logging.  The class can be multiple times.  Each instance can set up one of 
the following types of logs:

    CONSOLE:    prints all statements to either stdout or stderr depending on 
                the log level
    FILE:       uses the python logging module to log to specified files
    SYSLOG:     logs output to syslog


%prep
%setup -q -n cp_logging

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r ../cp_logging $RPM_BUILD_ROOT%{python_sitelib}


%files
%{python_sitelib}/cp_logging/

%changelog
* Mon May 06 2013 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.1
- initial packaging


