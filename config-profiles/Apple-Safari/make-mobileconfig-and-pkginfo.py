#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for programmatically generating a configuration
# profile with managed preferences for Apple Safari.
# Creates the profile, adds it to the munki repository (pkgs), then
# creates the pkginfo.
# Documentation & References: See closest ReadMe.md


# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28.
# 2016-10-24, 2016-12-02, 2017-01-20.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, plistlib, subprocess, sys

def make_mobileconfig():
    '''Generates a configuration profile with MCX, etc.'''

    # New profile main dict:
    mobileconfig_top_dict = {}
    mobileconfig_top_dict['PayloadVersion'] = int(1)
    mobileconfig_top_dict['PayloadType'] = "Configuration"
    mobileconfig_top_dict['PayloadScope'] = "System"
    mobileconfig_top_dict['PayloadIdentifier'] = "%s.profile.apple-safari" % ORGANIZATION_ID_PREFIX
    mobileconfig_top_dict['PayloadUUID'] = str(uuid.uuid4())
    mobileconfig_top_dict['PayloadOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mobileconfig_top_dict['PayloadDisplayName'] = CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME']
    mobileconfig_top_dict['PayloadDescription'] = CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION']
    mobileconfig_top_dict['PayloadContent'] = [] # This is an array of other dicts
    
    # com.apple.Safari:
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['HomePage'] = SAFARI_HOME_PAGE
    mcx_preference_settings_dict['NewWindowBehavior'] = int(0)
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.apple.Safari" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Safari Preferences"
    payload_mcx_dict['PayloadDescription'] = "Managed browser setting"
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.apple.Safari')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)

    return mobileconfig_top_dict

def make_managed_client_payload_content(given_mcx_preference_settings_dict,given_frequency,given_domain):
    '''Creates the tangled dict-dict-array-dict PayloadContent for a com.apple.ManagedClient.preferences payload.'''
    # Default:
    payload_content_dict = {}
    payload_content_dict[given_domain] = {}
    payload_content_dict[given_domain][given_frequency] = [{}]
    payload_content_dict[given_domain][given_frequency][0]['mcx_preference_settings'] = given_mcx_preference_settings_dict
    # Return:
    return payload_content_dict

def write_mobileconfig_and_add_to_repo(given_mobileconfig_dict):
    '''Writes the given mobileconfig to the working directory then imports it into munki.'''
    
    this_dir = os.path.dirname(os.path.realpath(__file__))
    print "Working dir is %s." % this_dir
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
    safari_name = raw_input("Name for this set of Safari prefs (no spaces): ").replace(' ','')
    CONFIG_PROFILE_FILE_NAME = "Configuration_Apple_Safari_%s.mobileconfig" % safari_name
    CONFIG_PROFILE_VERSION = raw_input("Profile version (example: 2016.10): ")
    PKGSINFO_FILE_NAME = "Configuration_Apple_Safari_%(safari_name)s-%(version)s" % {"safari_name":safari_name,"version":CONFIG_PROFILE_VERSION}
    global CONFIG_PROFILE_VARS_DICT, SAFARI_HOME_PAGE
    CONFIG_PROFILE_VARS_DICT = {}
    CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION'] = raw_input("Organization display name (example: Some State University): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME'] = raw_input("Profile display name (example: Safari Browser Settings): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION'] = raw_input("Profile description (example: From the IT Department): ")
    SAFARI_HOME_PAGE = raw_input("Safari home page URL (example: www.apple.com): ")

    # Generate mobileconfig:
    mobileconfig_dict = make_mobileconfig()
    # Write mobileconfig_contents to file:
    write_mobileconfig_and_add_to_repo(mobileconfig_dict)

if __name__ == "__main__":
    main()
