#!/usr/bin/env python

# make-pkginfo.py
# Script for generating pkginfo for deploying IBM SPSS via Munki.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24/28, 2015-09-11 (config profile and pkginfo creation), 2015-11-24 (conditions), 2015-11-25, 2015-12-07, 2016-03-21 (EndNote), 2016-07-28, 2016-08-30, 2016-10-03, 2016-11-09, 2016-11-14, 2016-11-29 (Autodesk), 2016-12-07.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys

# General variables; edit to suit your needs:
global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DESCRIPTION, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY, ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE
ITEM_MUNKI_NAME = "IBM_SPSS"
ITEM_MUNKI_DISP_NAME = "IBM SPSS"
ITEM_MUNKI_MIN_OS = "10.10.5"
ITEM_MUNKI_CATALOG_NAME = "software"
ITEM_MUNKI_DEVELOPER_NAME = "IBM"
ITEM_MUNKI_CATEGORY = "Math & Statistics"
ITEM_MUNKI_DESCRIPTION = "Installs IBM SPSS configured to use the license server."
# This script template is likely to require adjustment for each major IBM SPSS version:
ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE = '''#!/bin/bash
installer_bin="/private/tmp/SPSS_Statistics_Installer.bin"
license_data_file="/private/tmp/installer.properties"
license_data_content="
INSTALLER_UI=silent
LICENSE_ACCEPTED=true
network=1
InstallPython=1
LSHOST=__%app_license_server%__
COMMUTE_MAX_LIFE=7
COMPANYNAME=__%app_licensee%__
"
echo "$license_data_content" > "$license_data_file"

# Call vendor installer:
"$installer_bin" -f "$license_data_file"
if [ "$?" != "0" ]; then
    exit 1
fi

# Correct permissions:
/usr/sbin/chown -R root:admin "/Applications/IBM"
/bin/chmod -R 0775 "/Applications/IBM"

# Clean up:
if [ -f "$installer_bin" ]; then
    rm "$installer_bin"
fi
if [ -f "$license_data_file" ]; then
    rm "$license_data_file"
fi
'''

global ITEMS_TO_COPY
ITEMS_TO_COPY = []
COPY_ITEM_1 = {'destination_path':"/private/tmp",
'source_item':"SPSS_Statistics_Installer.bin",
'destination_item':"SPSS_Statistics_Installer.bin"}
ITEMS_TO_COPY.append(COPY_ITEM_1)

global ITEM_MUNKI_INSTALLS_ARRAY
ITEM_MUNKI_INSTALLS_ARRAY = []
ITEM_MUNKI_INSTALLS_ITEM = {}
ITEM_MUNKI_INSTALLS_ITEM['type'] = "application"
ITEM_MUNKI_INSTALLS_ITEM['path'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['CFBundleShortVersionString'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ARRAY.append(ITEM_MUNKI_INSTALLS_ITEM)

def create_items_to_copy_cmds():
    '''Converts an array of dicts describing items to copy into
    an array of args for makepkginfo.'''
    args = []
    for i_dict in ITEMS_TO_COPY:
        try:
            src_item_str = '--itemname=%s' % i_dict['source_item']
        except KeyError:
            src_item_str = ''
        try:
            dest_item_str = '--destinationitem=%s' % i_dict['destination_item']
        except KeyError:
            dest_item_str = ''
        try:
            dest_path_str = '--destinationpath=%s' % i_dict['destination_path']
        except KeyError:
            src_item_str = ''
        if dest_path_str and dest_item_str and dest_path_str:
            args.append(src_item_str)
            args.append(dest_item_str)
            args.append(dest_path_str)
    return args

def create_pkginfo(given_app_version,given_app_munki_installs_path,given_repo_path_to_pkg,given_app_license_server,given_app_licensee):
    '''Makes the pkginfo for this item.'''
    # Paths:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path
    # Postinstall script content:
    postinstall_script_content = ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE.replace("__%app_licensee%__",given_app_licensee).replace("__%app_license_server%__",given_app_license_server)
    # Call makepkginfo:
    cmd = ['/usr/local/munki/makepkginfo',
           '--name=%s' % ITEM_MUNKI_NAME,
           '--catalog=%s' % ITEM_MUNKI_CATALOG_NAME,
           '--description=%s' % ITEM_MUNKI_DESCRIPTION,
           '--developer=%s' % ITEM_MUNKI_DEVELOPER_NAME,
           '--category=%s' % ITEM_MUNKI_CATEGORY,
           '--unattended_install',
           '--pkgvers=%s' % given_app_version,
           '--displayname=%s' % ITEM_MUNKI_DISP_NAME]
    itc_args = create_items_to_copy_cmds()
    if not itc_args:
        return False
    cmd.extend(itc_args)
    cmd.append(munki_repo_pkg_path)
    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        print "Error creating pkginfo!"
        return False
    try:
        output_dict = plistlib.readPlistFromString(output)
    except xml.parsers.expat.ExpatError:
        return False
    # Other keys if defined:
    try:
        output_dict['minimum_os_version'] = ITEM_MUNKI_MIN_OS
    except NameError:
        pass
    try:
        output_dict['postinstall_script'] = postinstall_script_content
    except NameError:
        pass
    try:
        output_dict['installs'] = ITEM_MUNKI_INSTALLS_ARRAY
    except NameError:
        pass
    try:
        output_dict['installs'][0]['CFBundleShortVersionString'] = given_app_version
        output_dict['installs'][0]['path'] = given_app_munki_installs_path
    except KeyError, IndexError:
        pass

    plistlib.writePlist(output_dict,munki_repo_pkginfo_path)
    return True

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
    MUNKI_PKGSINFO_PATH = os.path.join(MUNKI_REPO_PATH,'pkgsinfo')

    # Gather item info:
    app_version = raw_input("SPSS version: ")
    app_munki_installs_path = raw_input("Path where app is installed (relative to client, should start with /Applications/IBM): ")
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)
    app_license_server = raw_input("License server hostname: ")
    app_licensee = raw_input("Licensee: ")

    # Generate pkginfo:
    if not create_pkginfo(app_version,app_munki_installs_path,repo_path_to_pkg,app_license_server,app_licensee):
        print "Failed to create pkginfo."
        sys.exit(1)
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
