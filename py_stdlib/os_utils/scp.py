import os

from openssh_wrapper import SSHConnection
from openssh_wrapper import SSHError

class SCPError(Exception): pass

class Scp(object):
    def __init__(self, hostname, port=None, username=None, ssh_key=None):
        self.host = hostname

        self.port = 22
        if port: self.port = port

        self.user = username
        self.ssh_key = ssh_key

    def source_exists(self, source):
        if not os.path.exists(source):
            raise IOError("Source file not found (%s)" % source)

    def scp(self, source, dest_path, mode):
        try:
            # Check to see if the source exists, raises ERROR_FILE_NOT_FOUND
            self.source_exists(source)

            # set up the ssh connection
            conn = SSHConnection(self.host, login=self.user, 
                                 port=self.port, identity_file=self.ssh_key)

            # scp the file
            conn.scp((source, ), target=dest_path, mode=mode, owner=self.user)
        except SSHError, ssh_e:
            raise SCPError("SCP failed: %s" % str(ssh_e))
