#!/usr/bin/env python

# preinstall.py
# Performs operations necessary before binding to Active Directory.
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24, 2016-05-31, 2016-06-13, 2017-05-08.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

# Variables:
global NTP_SERVER
NTP_SERVER = "__%NTP_SERVER%__"

import sys, plistlib, xml, subprocess, pwd, time

def osx_ntpdate(given_ntp_server):
    '''Calls ntpdate and attempts to update the system clock.
        Returns true if successful, false otherwise.'''
    try:
        subprocess.check_call(['/usr/sbin/ntpdate',
                                          '-u',
                                          given_ntp_server])
        return True
    except subprocess.CalledProcessError:
        return False

def remove_sys_keychain_override():
    '''Attempts to remove the DefaultKeychain key from
        /Library/Preferences/com.apple.security.plist.
        Using defaults here since the plist may be a binplist.'''
    plist_path = "/Library/Preferences/com.apple.security.plist"
    try:
        subprocess.check_call(['/usr/bin/defaults',
                               'delete',
                               plist_path,
                               'DefaultKeychain'])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    '''Main logic for preinstall'''
    # Set system clock using local NTP server if possible:
    if not osx_ntpdate(NTP_SERVER):
        print "Warning: Could not set system clock using %s." % NTP_SERVER
    # System keychain - remove custom default:
    if remove_sys_keychain_override():
        print "Removed custom DefaultKeychain key from com.apple.security.plist."
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
