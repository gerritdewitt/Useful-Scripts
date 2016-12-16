#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for programmatically generating a configuration
# profile with managed preferences for the Dock.
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28, 2015-09-01, 2016-06-02, 2016-12-13.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, os, uuid, plistlib, xml, subprocess

def make_mobileconfig(given_dock_name,given_dock_src_plist_dict):
    '''Generates a configuration profile with MCX, etc.'''

    # New profile main dict:
    mobileconfig_top_dict = {}
    mobileconfig_top_dict['PayloadVersion'] = int(1)
    mobileconfig_top_dict['PayloadType'] = "Configuration"
    mobileconfig_top_dict['PayloadScope'] = "System"
    mobileconfig_top_dict['PayloadIdentifier'] = "%(org)s.profile.dock.%(dock_name)s" % {"org":ORGANIZATION_ID_PREFIX, "dock_name":given_dock_name}
    mobileconfig_top_dict['PayloadUUID'] = str(uuid.uuid4())
    mobileconfig_top_dict['PayloadOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mobileconfig_top_dict['PayloadDisplayName'] = CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME']
    mobileconfig_top_dict['PayloadDescription'] = CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION']
    mobileconfig_top_dict['PayloadContent'] = [] # This is an array of other dicts
    
    # com.apple.dock: Custom Dock.
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.apple.dock" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Dock Content"
    payload_mcx_dict['PayloadDescription'] = "Provides custom Dock content."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(given_dock_src_plist_dict,'Forced','com.apple.dock')
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

def load_given_dock_plist_to_dict(given_dock_plist_path):
    '''Reads a given (potentially binary) com.apple.dock property list,
        returning its content as a dictionary.  Returns empty dict
        if something went wrong.'''
    if not os.path.exists(given_dock_plist_path):
        print "Error: %s does not exist" % given_dock_plist_path
        return {}
    # Convert plist to xml1:
    cmd = ['/usr/bin/plutil','-convert','xml1',given_dock_plist_path]
    try:
        subprocess.check_call(cmd)
        print "Converted %s to XML plist." % given_dock_plist_path
    except subprocess.CalledProcessError:
        print "Warning: failed to convert %s to XML plist (perhaps it is already)." % given_dock_plist_path
    # Try reading plist:
    try:
        dock_dict = plistlib.readPlist(given_dock_plist_path)
        return dock_dict
    except xml.parsers.expat.ExpatError:
        print "Error: failed to load %s!" % given_dock_plist_path
        return {}

def write_mobileconfig_and_add_to_repo(given_mobileconfig_dict,given_dock_src_plist_path,given_dock_name):
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
    dock_name = raw_input("Name for this Dock (no spaces): ").replace(' ','')
    CONFIG_PROFILE_FILE_NAME = "Configuration_Dock_%s.mobileconfig" % dock_name
    CONFIG_PROFILE_VERSION = raw_input("Profile version (example: 2016.10): ")
    PKGSINFO_FILE_NAME = "Configuration_Dock_%(dock_name)s-%(version)s" % {"dock_name":dock_name,"version":CONFIG_PROFILE_VERSION}
    global CONFIG_PROFILE_VARS_DICT
    CONFIG_PROFILE_VARS_DICT = {}
    CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION'] = raw_input("Organization display name (example: Some State University): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME'] = raw_input("Profile display name (example: Dock Settings): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION'] = raw_input("Profile description (example: From the IT Department): ")
    dock_src_plist_path = raw_input("Absolute path to source com.apple.dock.plist: ")

    # Read Dock plist to dict:
    dock_src_plist_dict = load_given_dock_plist_to_dict(dock_src_plist_path)
    if not dock_src_plist_dict:
        print "Cannot load Dock settings from %s!" % dock_src_plist_path
        sys.exit(1)

    # Generate mobileconfig:
    mobileconfig_dict = make_mobileconfig(dock_name,dock_src_plist_dict)
    # Write mobileconfig_contents to file and shove com.apple.dock content into the profile:
    write_mobileconfig_and_add_to_repo(mobileconfig_dict,dock_src_plist_path,dock_name)

if __name__ == "__main__":
    main()
