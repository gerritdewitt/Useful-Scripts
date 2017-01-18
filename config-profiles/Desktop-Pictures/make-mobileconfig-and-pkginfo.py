#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for programmatically generating a configuration profile
# to set the wallpaer to a PNG image at path:
# /Library/Desktop Pictures/Managed Desktop Picture.png
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28, 2015-09-11, 2016-06-03, 2016-12-13.
# 2017-01-17.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, plistlib, subprocess

def make_mobileconfig():
    '''Generates a configuration profile with MCX, etc.'''
    # New profile main dict:
    mobileconfig_top_dict = {}
    mobileconfig_top_dict['PayloadVersion'] = int(1)
    mobileconfig_top_dict['PayloadType'] = "Configuration"
    mobileconfig_top_dict['PayloadScope'] = "System"
    mobileconfig_top_dict['PayloadIdentifier'] = "%s.profile.desktop-picture-override" % ORGANIZATION_ID_PREFIX
    mobileconfig_top_dict['PayloadUUID'] = str(uuid.uuid4())
    mobileconfig_top_dict['PayloadOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mobileconfig_top_dict['PayloadDisplayName'] = CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME']
    mobileconfig_top_dict['PayloadDescription'] = CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION']
    mobileconfig_top_dict['PayloadContent'] = [] # This is an array of other dicts.
    
    # com.apple.desktop:
    payload_dict = {}
    payload_dict['PayloadVersion'] = int(1)
    payload_dict['PayloadType'] = "com.apple.desktop"
    payload_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_dict['PayloadIdentifier'] = "%s.payload.com.apple.desktop" % ORGANIZATION_ID_PREFIX
    payload_dict['PayloadDisplayName'] = "Managed Desktop Picture"
    payload_dict['PayloadDescription'] = "Defines a custom wallpaper."
    payload_dict['override-picture-path'] = "/Library/Desktop Pictures/Managed Desktop Picture.png"
    mobileconfig_top_dict['PayloadContent'].append(payload_dict)

    return mobileconfig_top_dict

def write_mobileconfig_and_add_to_repo(given_mobileconfig_dict):
    '''Writes the given mobileconfig to the working directory then imports it into munki.'''
    mobileconfig_file_path = os.path.join(MUNKI_PKGS_PATH,CONFIG_PROFILE_FILE_NAME)
    plistlib.writePlist(given_mobileconfig_dict,mobileconfig_file_path)
    print "Wrote mobileconfig to %s." % mobileconfig_file_path
    pkginfo_file_path = os.path.join(MUNKI_PKGSINFO_PATH,PKGSINFO_FILE_NAME)
    print "Pkginfo will be %s." % pkginfo_file_path

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % CONFIG_PROFILE_FILE_NAME,
                                          '--catalog=configuration',
                                          '--unattended_install',
                                          '--pkgvers=%s' % CONFIG_PROFILE_VERSION,
                                          mobileconfig_file_path])
        output_dict = plistlib.readPlistFromString(output)
        plistlib.writePlist(output_dict,pkginfo_file_path)
    except subprocess.CalledProcessError:
        print "Error creating pkginfo!"

def main():
    '''Main logic.'''
    # Gather Munki repository info:
    global MUNKI_REPO_PATH, MUNKI_PKGS_PATH, MUNKI_PKGSINFO_PATH
    try:
        MUNKI_REPO_PATH = os.environ['MUNKI_REPO_PATH']
    except KeyError:
        MUNKI_REPO_PATH = raw_input("Munki repo base path: ")
    if not os.path.exists(MUNKI_REPO_PATH):
        print "Munki repository does not exist at %s!" % MUNKI_REPO_PATH
        sys.exit(1)
    MUNKI_PKGS_PATH = os.path.join(MUNKI_REPO_PATH,'pkgs')
    if not os.path.exists(MUNKI_PKGS_PATH):
        print "Missing pkgs dir at %s!" % MUNKI_PKGS_PATH
        sys.exit(1)
    MUNKI_PKGSINFO_PATH = os.path.join(MUNKI_REPO_PATH,'pkgsinfo')
    if not os.path.exists(MUNKI_PKGSINFO_PATH):
        print "Missing pkgsinfo dir at %s!" % MUNKI_PKGSINFO_PATH
        sys.exit(1)

    # Gather item info:
    global ORGANIZATION_ID_PREFIX
    try:
        ORGANIZATION_ID_PREFIX = os.environ['ORGANIZATION_ID_PREFIX']
    except KeyError:
        ORGANIZATION_ID_PREFIX = raw_input("Organization prefix (example: org.sample): ")
    global CONFIG_PROFILE_FILE_NAME, CONFIG_PROFILE_VERSION, PKGSINFO_FILE_NAME
    CONFIG_PROFILE_FILE_NAME = "Configuration_Desktop_Picture_Managed.mobileconfig"
    CONFIG_PROFILE_VERSION = raw_input("Profile version (example: 2016.10): ")
    PKGSINFO_FILE_NAME = "Configuration_Desktop_Picture_Managed-%s" % CONFIG_PROFILE_VERSION
    global CONFIG_PROFILE_VARS_DICT
    CONFIG_PROFILE_VARS_DICT = {}
    CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION'] = raw_input("Organization display name (example: Some State University): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME'] = raw_input("Profile display name (example: Managed Desktop Picture): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION'] = raw_input("Profile description (example: From the IT Department): ")

    # Generate mobileconfig:
    mobileconfig_dict = make_mobileconfig()
    # Write mobileconfig_contents to file:
    write_mobileconfig_and_add_to_repo(mobileconfig_dict)

if __name__ == "__main__":
    main()
