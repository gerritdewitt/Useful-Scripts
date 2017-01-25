#!/usr/bin/env python

# installcheck.py
# Script for checking various Wi-Fi parameters:
# * DisconnectOnLogout: no
# * JoinMode: automatic
# * RememberRecentNetworks: no
# * RequireAdminPowerToggle: yes
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16, 2016-08-29.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, plistlib, xml, subprocess, os

def osx_airportd_verify_prefs(given_prefs_list):
    '''Returns true iff Wi-Fi prefs match the sufficient given list.'''
    # Run airportd and parse output:
    output = ''
    try:
        process = subprocess.Popen(['/usr/libexec/airportd',
                                    'prefs'],
                                   shell = False,
                                   bufsize = 1,
                                   stdout = subprocess.PIPE,
                                   stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError:
        process = None
    if process:
        while True:
            line = process.stdout.readline().decode()
            output += line
            if not line:
                break
    # Parse - create dict of key/values inferred from airportd:
    output_lines = output.split('\n')
    output_dict = {}
    for line in output_lines:
        pref_key = None
        pref_value = None
        line_kv = line.split('=')
        try:
            pref_key = line_kv[0].lower()
            pref_value = line_kv[1].lower()
        except IndexError:
            pass
        if pref_key and pref_value:
            output_dict[pref_key] = pref_value
    # Read through output dict, comparing prefs:
    result_list = []
    for pref_line in given_prefs_list:
        pref_key = None
        expected_value = None
        measured_value = None
        line_kv = pref_line.split('=')
        try:
            pref_key = line_kv[0].lower()
            expected_value = line_kv[1].lower()
        except IndexError:
            pass
        if pref_key and expected_value:
            try:
                measured_value = output_dict[pref_key]
            except KeyError:
                pass
            if measured_value == expected_value:
                result_list.append(True)
            else:
                result_list.append(False)
    # Nonempty result list without false values:
    if result_list and (False not in result_list):
        return True
    else:
        return False

def main():
    '''Main logic for this script'''
    prefs_list = ['DisconnectOnLogout=NO',
                  'JoinMode=Automatic',
                  'RememberRecentNetworks=No',
                  'RequireAdminPowerToggle=Yes']
    if not osx_airportd_verify_prefs(prefs_list):
        sys.exit(0) # "install" requested
    else:
        sys.exit(1) # all configured, skip

# Run main.
if __name__ == "__main__":
    main()
