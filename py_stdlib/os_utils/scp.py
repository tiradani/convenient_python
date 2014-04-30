import os

from openssh_wrapper import SSHConnection
from openssh_wrapper import SSHError

from hash_utils import checksum

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

            # get the sha256 checksum of the source file
            sha256_checksum = checksum(source)

            # set up the ssh connection
            conn = SSHConnection(self.host, login=self.user, 
                                 port=self.port, identity_file=self.ssh_key)

            # scp the file
            conn.scp((source, ), target=dest_path, mode=mode, owner=self.user)

            # Now get the sha256 checksum of the remote file
            command = "/usr/bin/sha256sum %s/%s" % (dest_path, os.path.basename(source))
            ret = conn.run(command)
            try:
                # the shell utility return the checksum + the file path, we only want the checksum
                remote_checksum = ret.stdout.split()[0]
                if sha256_checksum != remote_checksum:
                    raise SSHError("Checksums do not match.")
            except IndexError:
                raise SSHError("SCP failed:\n  Command: %s\n  stdout: %s\n  stderr: %s" % \
                               (command, ret.stdout, ret.stderr))

        except SSHError, ssh_e:
            raise SCPError("SCP failed: %s" % str(ssh_e))

