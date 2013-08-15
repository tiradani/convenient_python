import socket

from compat_subprocess import *
from daemonize import *
from file_utils import *
from ipaddr import *
from openssh_wrapper import *
from scp import *
from user_utils import *


def get_host():
    """
    Returns host information.

    @rtype: C{tuple}
    @param: A tuple containing the host name, the ip address, and the fully
    qualified domain name.
    """
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    fqdn = socket.getfqdn()

    return (hostname, ip_addr, fqdn)
