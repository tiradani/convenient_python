%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif


Name:           python_fstab
Group:          System Environment/Libraries
Version:        0
Release:        1%{?dist}
Summary:        Helper module for fstab files.

License:        GNU General Public License (version 3)
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel

Provides:       python_fstab = %{version}-%{release}

Source:         python_fstab.tar.gz


%description

Provides python-fstab module for reading and editing fstab files in python.  The
package was apparently written for and subsequently removed from Ubuntu/Debian.
The source has been modified to include more properties.  The original source 
for this package can be found at:

https://github.com/ProteinSimple/python-fstab


%prep
%setup -q -n python_fstab

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{python_sitelib}
cp -r ../python_fstab $RPM_BUILD_ROOT%{python_sitelib}


%files
%{python_sitelib}/python_fstab/

%changelog
* Mon May 06 2013 Anthony Tiradani <tiradani@fnal.gov> - 0.1
- initial packaging


