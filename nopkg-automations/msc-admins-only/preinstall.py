#!/usr/bin/env python

# preinstall.py
# Script for adjusting permissions on
# Managed Software Center to match a desired set.
# Useful if you need to restrict access to the app.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16.
# 2017-01-30, 2017-02-16, 2017-02-20.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, os, stat, logging

global MSC_PATH
MSC_PATH = '/Applications/Managed Software Center.app'
global MSC_OWNER_ID, MSC_GROUP_ID, MSC_MODE
MSC_OWNER_ID = int(0) # root
MSC_GROUP_ID = int(80) # admin
MSC_MODE = 0750 # octal

def set_perms(given_path,given_owner,given_group,given_mode):
    '''Attempts to set the owner, group, and mode for the given path. Returns true/false.'''
    # Try setting owner and group:
    try:
        os.chown(given_path,given_owner,given_group)
    except OSError:
        return False
    # Try setting POSIX bits:
    try:
        os.chmod(given_path,MSC_MODE)
    except OSError:
        return False
    # Return true if we got this far:
    return True

def main():
    '''Main logic for this script'''
    if not set_perms(MSC_PATH,MSC_OWNER_ID,MSC_GROUP_ID,MSC_MODE):
        logging.error("Failed to set permissions to 0750 on %s." % MSC_PATH)
        sys.exit(1)
    print "Set permissions to 0750 on %s." % MSC_PATH
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
