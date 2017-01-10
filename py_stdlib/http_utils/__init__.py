import os
import socket
import sys
import urlparse

from httplib import HTTPConnection
from py_stdlib import _under_24
from py_stdlib import _under_26
from urllib2 import build_opener
from urllib2 import install_opener
from urllib2 import HTTPHandler
from urllib2 import urlopen

def wget(url, saveas=""):
    u = urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if saveas:
        filename = saveas

    with open(filename, 'wb') as f:
        block_sz = 8192
        while True:
            read_buffer = u.read(block_sz)
            if not read_buffer: break
            f.write(read_buffer)

    return filename

#
#---------------- define timeout on urllib2 socket ops -------------#
#  Adapted from http://code.google.com/p/timeout-urllib2/

def sethttptimeout(timeout):
    """Use TimeoutHTTPHandler and set the timeout value.

    Args:
        timeout: the socket connection timeout value.
    """
    if _under_26():
        opener = build_opener(TimeoutHTTPHandler(timeout))
        install_opener(opener)
    else:
        raise Error("This python version has timeout builtin")

def _clear(sock):
    sock.close()
    return None

class Error(Exception): pass

class HTTPConnectionTimeoutError(Error): pass

class TimeoutHTTPConnection(HTTPConnection):
    """A timeout control enabled HTTPConnection.

    Inherit httplib.HTTPConnection class and provide the socket timeout
    control.
    """
    _timeout = None

    def __init__(self, host, port=None, strict=None, timeout=None):
        """Initialize the object.

        Args:
            host: the connection host.
            port: optional port.
            strict: strict connection.
            timeout: socket connection timeout value.
        """
        HTTPConnection.__init__(self, host, port, strict)
        self._timeout = timeout or TimeoutHTTPConnection._timeout
        if self._timeout: self._timeout = float(self._timeout)

    def connect(self):
        """Perform the socket level connection.

        A new socket object will get built everytime. If the connection
        object has _timeout attribute, it will be set as the socket
        timeout value.

        Raises:
          HTTPConnectionTimeoutError: when timeout is hit
          socket.error: when other general socket errors encountered.
        """
        msg = "getaddrinfo returns an empty list"
        err = socket.error
        for res in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                try:
                    self.sock = socket.socket(af, socktype, proto)
                    if self._timeout: self.sock.settimeout(self._timeout)
                    if self.debuglevel > 0:
                        print "connect: (%s, %s)" % (self.host, self.port)
                    self.sock.connect(sa)
                except socket.timeout, msg:
                    err = socket.timeout
                    if self.debuglevel > 0:
                        print 'connect timeout:', (self.host, self.port)
                    self.sock = _clear(self.sock)
                    continue
                break
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'general connect fail:', (self.host, self.port)
                self.sock = _clear(self.sock)
                continue
            break
        if not self.sock:
            if err == socket.timeout:
                raise HTTPConnectionTimeoutError, msg
            raise err, msg

class TimeoutHTTPHandler(HTTPHandler):
    """A timeout enabled HTTPHandler for urllib2."""
    def __init__(self, timeout=None, debuglevel=0):
        """Initialize the object.

        Args:
          timeout: the socket connect timeout value.
          debuglevel: the debuglevel level.
        """
        HTTPHandler.__init__(self, debuglevel)
        TimeoutHTTPConnection._timeout = timeout

    def http_open(self, req):
        """Use TimeoutHTTPConnection to perform the http_open"""
        return self.do_open(TimeoutHTTPConnection, req)

#---------------- end timeout on socket ops ----------------#
