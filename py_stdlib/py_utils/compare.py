#!/usr/bin/env python

import os
import sys
import filecmp
import shutil
import smtplib
import datetime

# ------------------------------------------------------------------
# Performs comparison operations on old and new password files
# ------------------------------------------------------------------
class DictOperations(object):
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(k for k in self.intersect if self.past_dict[k] != self.current_dict[k])
    def unchanged(self):
        return set(k for k in self.intersect if self.past_dict[k] == self.current_dict[k])

# ------------------------------------------------------------------
# Performs comparison operations on old and new password files
# ------------------------------------------------------------------
def isDifferent(old_file, new_file):
    return filecmp.cmp(old_file, new_file)

# ------------------------------------------------------------------
# Generates a dictionary from a file where each line is in the format:
#   key delimiter value
# ------------------------------------------------------------------
def generate_dict_from_file(file, dict, delimiter=':', comment='#'):
    if os.path.exists(file):
        try:
            f = open(file, 'rt')
            for line in f:
                if line.startswith(comment):
                    continue
                else:
                    (key, value) = line.split(delimiter)
                    dict[key] = value
            f.close()
        except Exception, ex:
            print ex
