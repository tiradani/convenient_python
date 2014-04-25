#!/usr/bin/env python

import datetime
import math
import os
import sys
import time

from py_stdlib.os_utils import check_output
from py_stdlib.os_utils import CalledProcessError
from py_stdlib.os_utils import head


class _X509(object):
    """
    Base X509 object.  Doesn't really do much but define some commonality
    between 'real' objects.
    """
    def __init__(self, path):
        super(_X509, self).__init__()
        self._path = path
        self._valid_time_units = ['seconds', 'minutes', 'days']

    @property
    def path(self):
        return self._path

    def _expires_in(self, expiration_timestamp, time_units='seconds'):
        eol = time.mktime(time.strptime(expiration_timestamp, "%b %d %H:%M:%S %Y GMT"))
        today = time.mktime(datetime.datetime.utcnow().timetuple())
        seconds_until_epiry = eol - today
        
        if not seconds_until_epiry == 0:
            if time_units in self._valid_time_units:
                if time_units == 'seconds':
                    expires_in = seconds_until_epiry
                elif time_units == 'minutes':
                    expires_in = int(math.floor(seconds_until_epiry / 60))
                elif time_units == 'hours':
                    expires_in = int(math.floor(seconds_until_epiry / 3600))
                elif time_units == 'days':
                    expires_in = int(math.floor(seconds_until_epiry / 86400))
        else:
            expires_in = seconds_until_epiry

        return expires_in

class X509Key(_X509):
    def __init__(self, key_path):
        super(X509Key, self).__init__(key_path)

        if not self.is_key(self._path):
            raise Exception("The file specified is not an X509 Key.")
            
    def is_key(self, cert_file):
        key_def = '-----BEGIN RSA PRIVATE KEY-----'
        first_line = head(cert_file)[0]
        if first_line.strip() == key_def: return True
        return False

class X509Certificate(_X509):
    def __init__(self, cert_path):
        super(X509Certificate, self).__init__(cert_path)

        self._service = None
        self._subject = None
        self._not_before = None
        self._not_after = None
        self._signature_algorithm = None

        if self.is_cert(cert_path):
            self._parse_certificate()
        else:
            raise Exception("The file specified is not an X509 certificate.")

    @property
    def service(self):
        return self._service

    @property
    def subject(self):
        return self._subject

    @property
    def not_before(self):
        return self._not_before

    @property
    def not_after(self):
        return self._not_after

    @property
    def signature_algorithm(self):
        return self._signature_algorithm

    def _extract_service(self, cert_subject):
        """
        example subject:
            /DC=com/DC=DigiCert-Grid/O=Open Science Grid/OU=Services/CN=<service name>/<host fqdn>
        we want the <service name>
        example subject 2:
            /DC=com/DC=DigiCert-Grid/O=Open Science Grid/OU=Services/CN=<host fqdn>
        in this case no service is specified, so service == host
        """
        pieces = cert_subject.split(',')
        # Get the second to last part of the DN.  If it begins with CN, then there is a service, if not, service == host
        service_name = pieces[len(pieces) - 2]
        service_name = service_name.split('=')
        if service_name[0] == 'CN':
            return service_name[1]
        else:
            return 'host'

    def _parse_certificate(self):
        # execute openssl command and get output
        command = ['/usr/bin/openssl', 'x509', '-noout', '-text', '-certopt', 'no_signame', '-in', self._path]
        output = check_output(command)

        output = output.split("\n")
        for line in output:
            parts = line.split(': ')
            if len(parts) > 1:
                key = parts[0].strip()
                value = parts[1].strip()
                if key == 'Signature Algorithm':
                    self._signature_algorithm = value
                elif key == 'Not Before':
                    self._not_before = value
                elif key == 'Not After':
                    self._not_after = value
                elif key == 'Subject':
                    raw_subject = value
                    self._service = self._extract_service(raw_subject)
                    self._subject = "/%s" % raw_subject.replace(', ', '/')

    def is_cert(self, cert_file):
        head_lines = head(cert_file, 3)
        for line in head_lines:
            if line.strip() == '-----BEGIN CERTIFICATE-----':
                return True
        return False

    def expires_in(self, units='seconds'):
        return self._expires_in(self._not_after, time_units=units)

    def __str__(self):
        expires_in_days = str(self.expires_in(units='days'))
        string_representation = """Host Certificate:
    Path: %s
    Service: %s
    Subject: %s
    Not Before: %s
    Not After: %s
    Signature Algorithm: %s
    Expires in (Days): %s
""" % (self._path, self._service, self._subject, self._not_before, self._not_after, 
       self._signature_algorithm, expires_in_days)

        return string_representation

class X509Crl(_X509):
    def __init__(self, crl_path):
        super(X509Crl, self).__init__(crl_path)

        self._issuer = None
        self._last_update = None
        self._next_update = None
        self._signature_algorithm = None
        self._revoked_certificates = []

        if self.is_crl(crl_path):
            self._parse_crl()
        else:
            raise Exception("The file specified is not a certificate.")

    @property
    def issuer(self):
        return self._issuer

    @property
    def last_update(self):
        return self._last_update

    @property
    def next_update(self):
        return self._next_update

    @property
    def revoked_certificates(self):
        return self._revoked_certificates

    @property
    def signature_algorithm(self):
        return self._signature_algorithm

    def is_crl(self, cert_file):
        first_line = head(cert_file)[0]
        if first_line.strip() == '-----BEGIN X509 CRL-----':
            return True
        return False

    def _parse_crl(self):
        # execute openssl command and get output
        command = ['/usr/bin/openssl', 'crl', '-noout', '-text', '-in', self.path]
        output = check_output(command)

        in_revoked_list = False
        revoked_dict = None
        output = output.split("\n")
        for line in output:
            parts = line.split(': ')
            if len(parts) > 0:
                key = parts[0].strip()
            if len(parts) > 1:
                value = parts[1].strip()

            if key == 'Issuer':
                self._issuer = value.strip()
            elif key == 'Last Update':
                self._last_update = value.strip()
            elif key == 'Next Update':
                self._next_update = value.strip()
            elif not in_revoked_list and key == 'Signature Algorithm':
                self._signature_algorithm = value.strip()

            # Now we get to the section where we parse out the revoked certificate information
            elif key == 'No Revoked Certificates.':
                # we are done parsing the crl
                break

            # Hey! There are revoked certificates, lets parse
            elif key == 'Revoked Certificates:':
                in_revoked_list = True
            elif in_revoked_list and key == 'Serial Number':
                revoked_dict = {'serial_number': value.strip()}
            elif in_revoked_list and key == 'Revocation Date':
                revoked_dict['revocation_date'] = value.strip()
                self._revoked_certificates.append(revoked_dict)

    def expires_in(self, units='seconds'):
        return self._expires_in(self._next_update, time_units=units)

    def __str__(self):
        revoked_certs = ""
        for cert in self._revoked_certificates:
            revoked_certs += "        Serial Number: %s - Revoked: %s\n" % (cert['serial_number'], cert['revocation_date'])

        string_representation = """CRL:
    Path: %s
    Issuer: %s
    Last Update: %s
    Next Update: %s
    Signature Algorithm: %s
    Revoked Certificates:"
%s
""" % (self._path, self._issuer, self._last_update, self._next_update, 
       self._signature_algorithm, revoked_certs)

        return string_representation

def get_hash_from_name(file_path):
    """
    Please note that there is absolutely no error checking in this function.
    All paths are assumed to end in 'file_name.extension'.  It is also assumed
    that the file_name is, in fact, the hash and not some other name.
    """
    return os.path.basename(file_path).split('.')[0]


def main():
    host_cert_path = '/etc/grid-security/hostcert.pem'
    host_cert = X509Certificate(host_cert_path)
    print host_cert

    print
    print

    crl_path = '/etc/grid-security/certificates/c7a717ce.r0'
    crl = X509Crl(crl_path)
    print crl

if __name__ == "__main__":
    sys.exit(main())
