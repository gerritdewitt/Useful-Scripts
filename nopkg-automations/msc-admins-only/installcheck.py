#!/usr/bin/env python

# installcheck.py
# Script for checking permissions on
# Managed Software Center against a desired set.
# Useful if you need to restrict access to the app.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16, 2016-08-29.
# 2017-01-30, 2017-02-16, 2017-02-20.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, os, stat

global MSC_PATH
MSC_PATH = '/Applications/Managed Software Center.app'
global MSC_OWNER_ID, MSC_GROUP_ID, MSC_MODE
MSC_OWNER_ID = int(0) # root
MSC_GROUP_ID = int(80) # admin
MSC_MODE = "0750" # str representation of four octal numbers

def verify_perms(given_path,given_owner,given_group,given_mode):
    '''Checks to see if the owner, group, and mode match for the given path. Returns true/false.'''
    s = os.stat(given_path)
    owner_ok = False
    group_ok = False
    mode_ok = False
    try:
        if s.st_uid == given_owner:
            owner_ok = True
    except AttributeError:
        pass
    try:
        if s.st_gid == given_group:
            group_ok = True
    except AttributeError:
        pass
    try:
        perms_as_decimal = stat.S_IMODE(s.st_mode)
        if str(oct(perms_as_decimal)) == given_mode:
            mode_ok = True
    except AttributeError:
        pass
    # Return:
    return (owner_ok and group_ok and mode_ok)

def main():
    '''Main logic for this script'''
    # Check for app:
    if not os.path.exists(MSC_PATH):
        sys.exit(1) # skip because the app is not present

    # Here if the app exists:
    if verify_perms(MSC_PATH,MSC_OWNER_ID,MSC_GROUP_ID,MSC_MODE):
        sys.exit(1) # skip because the perms are OK

    # Here if perms should be adjusted:
    print "Permissions on %s should be adjusted (desired state 0750)." % MSC_PATH
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
