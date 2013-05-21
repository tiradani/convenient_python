%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           cp_os_utils
Group:          System Environment/Libraries
Version:        0
Release:        1%{?dist}
Summary:        Provides python implementations of many shell commands.

License:        Fermitools Software Legal Information (Modified BSD License)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       cp_os_utils = %{version}-%{release}

Source:         cp_os_utils.tar.gz


%description
Provides python implementations of many shell commands.


%prep
%setup -q -n cp_os_utils

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r ../cp_os_utils $RPM_BUILD_ROOT%{python_sitelib}


%files
%{python_sitelib}/cp_os_utils/

%changelog
* Mon May 06 2013 Anthony Tiradani <anthony.tiradani@gmail.com> - 0.1
- initial packaging


