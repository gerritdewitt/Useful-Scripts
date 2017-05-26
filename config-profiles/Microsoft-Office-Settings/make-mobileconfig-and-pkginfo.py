#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for programmatically generating a configuration
# profile with managed preferences for Microsoft Office.
# Creates the profile, adds it to the munki repository (pkgs), then
# creates the pkginfo.
# Documentation & References: See closest ReadMe.md


# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28.
# 2016-10-24, 2016-12-02.
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
    mobileconfig_top_dict['PayloadIdentifier'] = "%(org)s.config.profile.microsoft-office" % {"org":ORGANIZATION_ID_PREFIX}
    mobileconfig_top_dict['PayloadUUID'] = str(uuid.uuid4())
    mobileconfig_top_dict['PayloadOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mobileconfig_top_dict['PayloadDisplayName'] = CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME']
    mobileconfig_top_dict['PayloadDescription'] = CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION']
    mobileconfig_top_dict['PayloadContent'] = [] # This is an array of other dicts
    
    # com.microsoft.autoupdate2: Prevents alerts for Office 2011 updates.
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['HowToCheck'] = "Manual"
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.autoupdate2" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Office 2011 Update Notifications"
    payload_mcx_dict['PayloadDescription'] = "Prevents alerts for Office 2011 updates."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.autoupdate2')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)
    
    # com.microsoft.error_reporting: Prevents various alerts for Office 2011.
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['SQMReportsEnabled'] = False
    mcx_preference_settings_dict['ShipAssertEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.error_reporting" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Office 2011 Error Reporting"
    payload_mcx_dict['PayloadDescription'] = "Prevents various alerts for Office 2011."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.error_reporting')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)
    
    # com.microsoft.office: Prevents setup alerts for Office 2011.
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['14\FirstRun\SetupComplete'] = int(1)
    mcx_preference_settings_dict['14\UserInfo\UserName'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mcx_preference_settings_dict['14\UserInfo\UserOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.office" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Office 2011 Registration"
    payload_mcx_dict['PayloadDescription'] = "Prevents setup alerts for Office 2011."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.office')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)
    
    # com.microsoft.Outlook: For Outlook 2016
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['kSubUIAppCompletedFirstRunSetup1507'] = True
    mcx_preference_settings_dict['FirstRunExperienceCompletedO15'] = True
    mcx_preference_settings_dict['SendAllTelemetryEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.Outlook" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Outlook 2016 First Run Suppression"
    payload_mcx_dict['PayloadDescription'] = "Suppresses first run and reporting in Outlook 2016."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.Outlook')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)

    # com.microsoft.onenote.mac: For OneNote 2016
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['kSubUIAppCompletedFirstRunSetup1507'] = True
    mcx_preference_settings_dict['FirstRunExperienceCompletedO15'] = True
    mcx_preference_settings_dict['SendAllTelemetryEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.OneNote" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "OneNote 2016 First Run Suppression"
    payload_mcx_dict['PayloadDescription'] = "Suppresses first run and reporting in OneNote 2016."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.onenote.mac')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)  
    
    # com.microsoft.PowerPoint: For PowerPoint 2016
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['kSubUIAppCompletedFirstRunSetup1507'] = True
    mcx_preference_settings_dict['SendAllTelemetryEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.PowerPoint" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "PowerPoint 2016 First Run Suppression"
    payload_mcx_dict['PayloadDescription'] = "Suppresses first run and reporting in PowerPoint 2016."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.PowerPoint')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)
        
    # com.microsoft.Excel: For Excel 2016
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['kSubUIAppCompletedFirstRunSetup1507'] = True
    mcx_preference_settings_dict['SendAllTelemetryEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.Excel" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Excel 2016 First Run Suppression"
    payload_mcx_dict['PayloadDescription'] = "Suppresses first run and reporting in Excel 2016."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.Excel')
    mobileconfig_top_dict['PayloadContent'].append(payload_mcx_dict)
            
    # com.microsoft.Word: For Word 2016
    mcx_preference_settings_dict = {}
    mcx_preference_settings_dict['kSubUIAppCompletedFirstRunSetup1507'] = True
    mcx_preference_settings_dict['SendAllTelemetryEnabled'] = False
    payload_mcx_dict = {}
    payload_mcx_dict['PayloadVersion'] = int(1)
    payload_mcx_dict['PayloadType'] = "com.apple.ManagedClient.preferences"
    payload_mcx_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_mcx_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.ManagedClient.preferences.com.microsoft.Word" % ORGANIZATION_ID_PREFIX
    payload_mcx_dict['PayloadDisplayName'] = "Word 2016 First Run Suppression"
    payload_mcx_dict['PayloadDescription'] = "Suppresses first run and reporting in Word 2016."
    payload_mcx_dict['PayloadContent'] = make_managed_client_payload_content(mcx_preference_settings_dict,'Forced','com.microsoft.Word')
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
    CONFIG_PROFILE_FILE_NAME = "Configuration_Microsoft_Office.mobileconfig"
    CONFIG_PROFILE_VERSION = raw_input("Profile version (example: 2016.10): ")
    PKGSINFO_FILE_NAME = "Configuration_Microsoft_Office-%s" % CONFIG_PROFILE_VERSION
    global CONFIG_PROFILE_VARS_DICT
    CONFIG_PROFILE_VARS_DICT = {}
    CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION'] = raw_input("Organization display name (example: Some State University): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME'] = raw_input("Profile display name (example: Microsoft Office Settings): ")
    CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION'] = raw_input("Profile description (example: From the IT Department): ")

    # Generate mobileconfig:
    mobileconfig_dict = make_mobileconfig()
    # Write mobileconfig_contents to file:
    write_mobileconfig_and_add_to_repo(mobileconfig_dict)

if __name__ == "__main__":
    main()
