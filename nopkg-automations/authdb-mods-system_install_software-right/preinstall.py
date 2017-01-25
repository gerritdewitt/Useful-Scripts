#!/usr/bin/env python

# preinstall.py
# Script for modifying the authorization policy database used by securityd
# for the purpose of allowing the session owner software installation rights.
# This script alters the system.install.software right,
# setting the session-owner key True.
# This has the effect of allowing the session user the freedom to install things
# but not mess with other configuration.
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

def macos_authdb_write_dict_to_right(given_right,given_right_dict):
    '''Sets the given authorization policy database right to the given dictionary.
        Returns true/false.'''
    # Parse:
    if given_right_dict:
        try:
            right_str = plistlib.writePlistToString(given_right_dict)
        except xml.parsers.expat.ExpatError:
            return False
    # Run security:
    try:
        process = subprocess.Popen(['/usr/bin/security',
                                    'authorizationdb',
                                    'write',
                                    given_right],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate(input=right_str)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    '''Main logic for this script'''
    # Read existing right:
    sec_right_dict = macos_authdb_read_right_to_dict('system.install.software')
    if not sec_right_dict:
        sys.exit(1)
    # Modify right:
    sec_right_dict['session-owner'] = True
    # Save right:
    if not macos_authdb_write_dict_to_right('system.install.software',sec_right_dict):
        sys.exit(1)
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
