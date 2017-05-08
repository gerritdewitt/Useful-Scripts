#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for programmatically generating a configuration
# profile for binding Mac systems to Active Directory.
# Creates the profile, adds it to the munki repository (pkgs), then
# creates the pkginfo.
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24, 2016-05-31, 2016-06-17, 2017-05-08.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, plistlib, subprocess

def make_active_directory_mobileconfig():
    '''Generates a configuration profile that joins Mac systems to Active Directory.'''

    # New profile main dict:
    mobileconfig_top_dict = {}
    mobileconfig_top_dict['PayloadVersion'] = int(1)
    mobileconfig_top_dict['PayloadType'] = "Configuration"
    mobileconfig_top_dict['PayloadScope'] = "System"
    mobileconfig_top_dict['PayloadIdentifier'] = "%(org)s.config.profile.active-directory" % {"org":ORGANIZATION_ID_PREFIX}
    mobileconfig_top_dict['PayloadUUID'] = str(uuid.uuid4())
    mobileconfig_top_dict['PayloadOrganization'] = CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION']
    mobileconfig_top_dict['PayloadDisplayName'] = CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME']
    mobileconfig_top_dict['PayloadDescription'] = CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION']
    mobileconfig_top_dict['PayloadContent'] = [] # This is an array of other dicts.
    
    # AD configuration:
    payload_ad_dict = {}
    payload_ad_dict['PayloadVersion'] = int(1)
    payload_ad_dict['PayloadType'] = "com.apple.DirectoryService.managed"
    payload_ad_dict['PayloadUUID'] = str(uuid.uuid4())
    payload_ad_dict['PayloadIdentifier'] = "%s.config.payload.com.apple.DirectoryService.managed" % ORGANIZATION_ID_PREFIX
    payload_ad_dict['PayloadDisplayName'] = "Active Directory Binding"
    payload_ad_dict['PayloadDescription'] = "Joins %s." % CONFIG_PROFILE_VARS_DICT['AD_FOREST']
    payload_ad_dict['HostName'] = CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_HOSTNAME']
    payload_ad_dict['UserName'] = CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_USERNAME']
    payload_ad_dict['Password'] = CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_PASSWORD']
    payload_ad_dict['ADCreateMobileAccountAtLoginFlag'] = True
    payload_ad_dict['ADCreateMobileAccountAtLogin'] = True
    payload_ad_dict['ADWarnUserBeforeCreatingMAFlag'] = True
    payload_ad_dict['ADWarnUserBeforeCreatingMA'] = False
    payload_ad_dict['ADForceHomeLocalFlag'] = True
    payload_ad_dict['ADForceHomeLocal'] = True
    payload_ad_dict['ADDomainAdminGroupListFlag'] = True
    if CONFIG_PROFILE_VARS_DICT['AD_OU']:
        payload_ad_dict['ADOrganizationalUnit'] = CONFIG_PROFILE_VARS_DICT['AD_OU']
    if CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST']:
        payload_ad_dict['ADDomainAdminGroupList'] = CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST']
    
    mobileconfig_top_dict['PayloadContent'].append(payload_ad_dict)

    return mobileconfig_top_dict

def write_mobileconfig_and_add_to_repo(given_mobileconfig_dict):
    '''Writes the given mobileconfig to the working directory then imports it into munki.'''
    
    this_dir = os.path.dirname(os.path.realpath(__file__))
    print "Working dir is %s." % this_dir
    item_munki_preinstall_script_path = os.path.join(this_dir,PREINSTALL_FILE_NAME)
    print "Expecting preinstall script at %s." % item_munki_preinstall_script_path
    mobileconfig_file_path = os.path.join(MUNKI_PKGS_PATH,CONFIG_PROFILE_FILE_NAME)
    plistlib.writePlist(given_mobileconfig_dict,mobileconfig_file_path)
    print "Wrote mobileconfig to %s." % mobileconfig_file_path
    pkginfo_file_path = os.path.join(MUNKI_PKGSINFO_PATH,PKGSINFO_FILE_NAME)
    print "Pkginfo will be %s." % pkginfo_file_path
    
    # Preinstall script content, if specified:
    if not ITEM_MUNKI_PREINSTALL_TEMPLATE_PATH:
        print "Error creating pkginfo!"
        sys.exit(1)
    
    h = open(ITEM_MUNKI_PREINSTALL_TEMPLATE_PATH,'r')
    preinstall_script_content = h.read()
    h.close()
    preinstall_script_content = preinstall_script_content.replace("__%NTP_SERVER%__",NTP_SERVER)
    item_munki_preinstall_script_path = "/private/tmp/%s_preinstall_script.py" % CONFIG_PROFILE_FILE_NAME
    h = open(item_munki_preinstall_script_path,'w')
    h.write(preinstall_script_content)
    h.close()


    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % CONFIG_PROFILE_FILE_NAME,
                                          '--catalog=configuration',
                                          '--unattended_install',
                                          '--pkgvers=%s' % CONFIG_PROFILE_VERSION,
                                          '--preinstall_script=%s' % item_munki_preinstall_script_path,
                                          mobileconfig_file_path])
        output_dict = plistlib.readPlistFromString(output)
        plistlib.writePlist(output_dict,pkginfo_file_path)
    except subprocess.CalledProcessError:
        print "Error creating pkginfo!"
        sys.exit(1)

def main():
    '''Main logic.'''
    # Gather Munki repository info:
    global PREINSTALL_FILE_NAME
    PREINSTALL_FILE_NAME = "preinstall.py"
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
    CONFIG_PROFILE_FILE_NAME = "Configuration_Active_Directory.mobileconfig"
    CONFIG_PROFILE_VERSION = raw_input("Profile version (example: 2016.10): ")
    PKGSINFO_FILE_NAME = "Configuration_Active_Directory-%s" % CONFIG_PROFILE_VERSION
    global CONFIG_PROFILE_VARS_DICT, NTP_SERVER, ITEM_MUNKI_PREINSTALL_TEMPLATE_PATH
    CONFIG_PROFILE_VARS_DICT = {}
    CONFIG_PROFILE_VARS_DICT['TOP_ORGANIZATION'] = raw_input("Organization display name (example: Some State University): ")
    CONFIG_PROFILE_VARS_DICT['AD_FOREST'] = raw_input("AD forest (example: forest.sample.org): ").strip()
    CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_HOSTNAME'] = raw_input("AD domain to join (example: dom.forest.sample.org): ").strip()
    CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_USERNAME'] = raw_input("User name for binding (e.g., service account name): ").strip()
    CONFIG_PROFILE_VARS_DICT['AD_DOMAIN_PASSWORD'] = raw_input("Password for binding user (e.g., service account password): ").strip()
    CONFIG_PROFILE_VARS_DICT['AD_OU'] = raw_input("Default OU for new computers (leave blank for Apple default):")
    CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST'] = []
    CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST'] = raw_input("Comma separated list of AD groups to grant local admin rights (leave blank for none): ")
    if ',' in CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST']:
        l = CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST'].split(',')
        CONFIG_PROFILE_VARS_DICT['AD_ADMIN_GROUP_LIST'] = [x for x in l if x]
    NTP_SERVER = raw_input("NTP server (example: ntp.sample.org): ").strip()
    CONFIG_PROFILE_VARS_DICT['TOP_DISPLAY_NAME'] = "Active Directory (%s)" % CONFIG_PROFILE_VARS_DICT['AD_FOREST']
    CONFIG_PROFILE_VARS_DICT['TOP_DESCRIPTION'] = raw_input("Profile description (example: From the IT Department): ")
    THIS_DIR = os.path.dirname(os.path.realpath(__file__))
    ITEM_MUNKI_PREINSTALL_TEMPLATE_PATH = os.path.join(THIS_DIR, "preinstall-template.py")


    # Generate mobileconfig:
    mobileconfig_dict = make_active_directory_mobileconfig()
    # Write mobileconfig_contents to file:
    write_mobileconfig_and_add_to_repo(mobileconfig_dict)

if __name__ == "__main__":
    main()
