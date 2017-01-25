#!/usr/bin/env python

# preinstall.py
# Script for setting various Wi-Fi parameters to control the behavior of
# Wi-Fi on laptops intended for computer labs.  Sets the following:
# * DisconnectOnLogout: disabled, should be a system default anyway
# * JoinMode: automatic, should be a system default anyway
# * RememberRecentNetworks: false; this prevents the Preferred Networks list
#   from adding recently used networks.
# * RequireAdminPowerToggle: true; this prevents a situation
#   where a previous user may deny Wi-Fi login to the next
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, subprocess, os

def osx_airportd_set_prefs(given_prefs_list):
    '''Sets various Wi-Fi prefs via airportd.'''
    airportd_cmd =['/usr/libexec/airportd',
                   'prefs']
    airportd_cmd.extend(given_prefs_list)
    try:
        subprocess.check_call(airportd_cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    '''Main logic for this script'''
    prefs_list = ['DisconnectOnLogout=NO',
                  'JoinMode=Automatic',
                  'RememberRecentNetworks=No',
                  'RequireAdminPowerToggle=Yes']
    if not osx_airportd_set_prefs(prefs_list):
        sys.exit(1)
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
