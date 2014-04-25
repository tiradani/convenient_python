#!/usr/bin/env python
# -*- Mode: python -*-

"""
This module provides an interface for the pssh utility.

sample config:

pssh:
  parallel_workers: 32
  timeout: 60
  askpass: False
  output_directory: /tmp/output
  error_directory: /tmp/errors
  host_files: /etc/pssh/hosts
  username: root
  verbose: False
  print_out: False
  recursive: True       # for pscp
  inline: False         # for pssh
  inline_stdout: False  # for pssh
  remote: /tmp/command

"""

import os

from psshlib import psshutil
from psshlib.manager import Manager, FatalError
from psshlib.task import Task

class PSSHOptions(object):
    def __init__(self, config, section):
        self.par = config["parallel_workers"]
        self.timeout = config["timeout"]
        self.askpass = config["askpass"]
        self.outdir = config["output_directory"]
        self.errdir = config["error_directory"]
        self.user = config["username"]
        self.host_files = config["host_files"]

        self.verbose = False
        self.print_out = False
        self.inline = False
        self.inline_stdout = False
        self.recursive = False

        self.verbose = config["verbose"]
        self.print_out = config["print_out"]
        if config["inline"]: self.inline = config["inline"]
        if config["inline_stdout"]: self.inline_stdout = config["inline_stdout"]
        if config["recursive"]: self.recursive = config["recursive"]
        if config["remote"]: self.remote = config["remote"]

        if self.outdir and not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        if self.errdir and not os.path.exists(self.errdir):
            os.makedirs(self.errdir)

def do_pssh(cmdline, pssh_config):
    rtn_code = 0

    options = PSSHOptions(pssh_config)
    hosts = psshutil.read_host_files(options.host_files, default_user='root')
    manager = Manager(options)

    for host, port, user in hosts:
        cmd = ['ssh', host, '-o', 'NumberOfPasswordPrompts=1',
                '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST']
        if user:
            cmd += ['-l', user]
        if port:
            cmd += ['-p', port]

        if cmdline:
            cmd.append(cmdline)

        t = Task(host, port, user, cmd, options)
        manager.add_task(t)
    try:
        statuses = manager.run()
    except FatalError:
        rtn_code = 1

    if min(statuses) < 0:
        # At least one process was killed.
        rtn_code = 3

    for status in statuses:
        if status == 255:
            rtn_code = 4

    for status in statuses:
        if status != 0:
            rtn_code = 5

    return rtn_code

def do_pscp(pssh_config):
    rtn_code = 0

    options = PSSHOptions(pssh_config)
    hosts = psshutil.read_host_files(options.host_files, default_user='root')

    manager = Manager(options)
    for host, port, user in hosts:
        cmd = ['scp', '-qC']
        if port:
            cmd += ['-P', port]
        if options.recursive:
            cmd.append('-r')
        if user:
            cmd.append('%s@%s:%s' % (user, host, options.remote))
        else:
            cmd.append('%s:%s' % (host, options.remote))
        cmd.append('%s' % options.outdir)
        t = Task(host, port, user, cmd, options)
        manager.add_task(t)
    try:
        statuses = manager.run()
    except FatalError:
        rtn_code = 1

    if min(statuses) < 0:
        # At least one process was killed.
        rtn_code = 3

    for status in statuses:
        if status != 0:
            rtn_code = 4

    return rtn_code

