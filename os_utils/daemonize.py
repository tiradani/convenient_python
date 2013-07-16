#!/usr/bin/python

"""
This code for the most part is a copy of daemonize.py from the daemonize project
at: https://github.com/thesharp/daemonize

The code is distributed under the MIT license.

There are a couple of slight modifications to make things slightly more explicit
and to properly set up lock files in the intended locations

Example usage:


import logging
from daemonize import Daemonize

pid = "/tmp/test.pid"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("/tmp/test.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]


def main():
    logger.debug("Test")

daemon = Daemonize(app="test_app", action=main, pid=pid, keep_fds=keep_fds)
daemon.start()


"""

import fcntl  # @UnresolvedImport
import os
import sys
import signal
import resource
import logging
import atexit
import errno
from logging import handlers


class Daemonize(object):
    """ 
    Daemonize object

    Object constructor expects three arguments:
        - app: contains the application name which will be sent to syslog.
        - pid: path to the pidfile.
        - action: your custom function which will be executed after daemonization.
        - keep_fds: optional list of fds which should not be closed.
    """
    def __init__(self, app, action, pid=None, keep_fds=None):
        self.app = app
        self.action = action
        if pid:
            self.pid = pid
        else:
            self.pid = "/var/lock/%s/pid_file.pid" % self.app
        self.pid_dir = os.path.dirname(self.pid)

        if keep_fds:
            self.keep_fds = keep_fds
        else:
            self.keep_fds = []
        # Initialize logging.
        self.logger = logging.getLogger(self.app)
        self.logger.setLevel(logging.DEBUG)
        # Display log messages only on defined handlers.
        self.logger.propagate = False

        # It will work on OS X and Linux. No FreeBSD support, guys, I don't want
        # to import re here to parse your peculiar platform string.
        if sys.platform == "darwin":
            syslog_address = "/var/run/syslog"
        else:
            syslog_address = "/dev/log"

        syslog = handlers.SysLogHandler(syslog_address)
        syslog.setLevel(logging.INFO)

        # Try to mimic to normal syslog messages.
        formatter = logging.Formatter("%(asctime)s %(name)s: %(message)s",
                                      "%b %e %H:%M:%S")
        syslog.setFormatter(formatter)
        self.logger.addHandler(syslog)

    def sigterm(self, signum, frame):
        """ 
        sigterm method

        These actions will be done after SIGTERM.
        """
        self.logger.warn("Caught signal %s. Stopping daemon." % signum)
        os.remove(self.pid)
        sys.exit(0)

    def create_pid_dir(self):
        try:
            os.makedirs(self.pid_dir)
        except OSError, ose:
            if ose.errno == errno.EEXIST:
                pass
            else:
                raise

    def start(self):
        """ 
        start method

        Main daemonization process.
        """
        # Fork, creating a new process for the child.
        process_id = os.fork()
        if process_id < 0:
            # Fork error. Exit badly.
            sys.exit(1)
        elif process_id != 0:
            # This is the parent process. Exit.
            sys.exit(0)
        # This is the child process. Continue.

        # Stop listening for signals that the parent process receives.
        # This is done by getting a new process id.
        # setpgrp() is an alternative to setsid().
        # setsid puts the process in a new parent group and detaches its 
        # controlling terminal.
        process_id = os.setsid()
        if process_id == -1:
            # Uh oh, there was a problem.
            sys.exit(1)

        # Close all file descriptors, except the ones mentioned in self.keep_fds
        devnull = "/dev/null"
        if hasattr(os, "devnull"):
            # Python has set os.devnull on this system, use it instead as it 
            # might be different than /dev/null.
            devnull = os.devnull

        for fd in range(resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
            if fd not in self.keep_fds:
                try:
                    os.close(fd)
                except OSError:
                    pass

        os.open(devnull, os.O_RDWR)
        
        os.dup(0, 1)
        os.dup(0, 2)

        # Set umask to default to safe file permissions when running as a root 
        # daemon. 027 is an octal number which we are typing as 0o27 for 
        # Python3 compatibility.
        os.umask(0o27)

        # Change to a known directory. If this isn't done, starting a daemon in 
        # a subdirectory that needs to be deleted results in "directory busy" 
        # errors.
        os.chdir("/")

        # We need to create, if possible, the pid dir
        try:
            self.create_pid_dir()
        except:
            error_message = "Unable to create pid directory (%s).\n\n" \
                            "Terminating now." % self.pid_dir
            self.logger.warn(error_message)
        # Create a lockfile so that only one instance of this daemon is running at any time.
        lockfile = open(self.pid, "w")
        # Try to get an exclusive lock on the file. This will fail if another process has the file
        # locked.
        fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # Record the process id to the lockfile. This is standard practice for daemons.
        lockfile.write("%s" % (os.getpid()))
        lockfile.flush()

        # Set custom action on SIGTERM.
        signal.signal(signal.SIGTERM, self.sigterm)
        atexit.register(self.sigterm)

        self.logger.warn("Starting daemon.")

        self.action()