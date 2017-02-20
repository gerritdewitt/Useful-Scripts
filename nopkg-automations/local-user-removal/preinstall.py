#!/usr/bin/env python

# preinstall.py
# Script for deleting a given local user account.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16.
# 2017-01-30.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, subprocess, os, logging

global LOCAL_USER_NAME
LOCAL_USER_NAME = 'local_account_name' # Replace with the name of your local user account to be purged.

def macos_delete_local_account(given_user_name):
    '''Returns true iff the given user account was
        deleted, false otherwise.'''
    try:
        subprocess.check_call(['/usr/bin/dscl',
                               '/Local/Default',
                               'delete',
                               '/Users/%s' % given_user_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    '''Main logic for this script'''
    if not macos_delete_local_account(LOCAL_USER_NAME):
        logging.error("Failed to delete %s." % LOCAL_USER_NAME)
        sys.exit(1)
    print "Deleted %s." % LOCAL_USER_NAME
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
