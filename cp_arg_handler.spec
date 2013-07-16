%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           cp_arg_handler
Group:          System Environment/Libraries
Version:        0
Release:        1%{?dist}
Summary:        Helper module for parsing command line options and arguments.

License:        Fermitools Software Legal Information (Modified BSD License)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       cp_arg_handler = %{version}-%{release}

Source:         arg_handler.tar.gz


%description
Provides a helper module for parsing command line options and arguments.


%prep
%setup -q -n arg_handler

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r ../arg_handler $RPM_BUILD_ROOT%{python_sitelib}


%files
%{python_sitelib}/cp_arg_handler/

%changelog
* Mon May 10 2013 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.1
- initial packaging


