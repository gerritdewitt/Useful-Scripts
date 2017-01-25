#!/usr/bin/env python

# installcheck.py
# This script returns 0 (install requested) when:
# (a) the system.install.software right exists, can be read, and
# (b) the session-owner key is in that right, and
# (c) the session-owner key False.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-10-19.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, subprocess, os, xml, plistlib

def macos_authdb_read_right_to_dict(given_right):
    '''Reads the given authorization policy database right.
        Returns a dict.'''
    right_dict = {}
    # Run security:
    try:
        output = subprocess.check_output(['/usr/bin/security',
                                          'authorizationdb',
                                          'read',
                                          given_right])
    except subprocess.CalledProcessError:
        output = ''
    # Parse:
    if output:
        try:
            right_dict = plistlib.readPlistFromString(output)
        except xml.parsers.expat.ExpatError:
            pass
    # Return:
    return right_dict

def main():
    '''Main logic for this script'''
    # Read existing right:
    sec_right_dict = macos_authdb_read_right_to_dict('system.install.software')
    if sec_right_dict:
        try:
            if not sec_right_dict['session-owner']:
                sys.exit(0) # "install" requested
        except KeyError:
            pass
    # Skip and do nothing:
    # (a) if right cannot be read, or
    # (b) if session-owner key not in right, or
    # (c) if session-owner key is in right and already True.
    sys.exit(1)
# Run main.
if __name__ == "__main__":
    main()
