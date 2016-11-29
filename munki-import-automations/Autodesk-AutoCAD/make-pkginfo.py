#!/usr/bin/env python

# make-pkginfo.py
# Script for generating pkginfo for deploying AutoDesk AutoCAD via Munki.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24/28, 2015-09-11 (config profile and pkginfo creation), 2015-11-24 (conditions), 2015-11-25 (Mathematica), 2015-11-30 (Maple), 2016-11-14, 2016-11-29.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, xml, plistlib, subprocess, sys

# General variables; edit to suit your needs:
global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DESCRIPTION, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY, ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE
ITEM_MUNKI_NAME = "Autodesk_AutoCAD"
ITEM_MUNKI_DISP_NAME = "Autodesk AutoCAD"
ITEM_MUNKI_MIN_OS = "10.10.5"
ITEM_MUNKI_CATALOG_NAME = "software" # catalog to which this item will be published
ITEM_MUNKI_DEVELOPER_NAME = "Autodesk"
ITEM_MUNKI_CATEGORY = "Autodesk"
ITEM_MUNKI_DESCRIPTION = "Installs Autodesk AutoCAD configured to use the license server."
# This script template is likely to require adjustment for each major AutoCAD version:
ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE = '''#!/bin/bash
license_data_file="/private/tmp/acodeAutoCAD2016"
license_data_content="__%app_serial%__
__%app_prod_key%__
Single_License_Server
__%app_license_server%__
US"
echo "$license_data_content" > "$license_data_file"
'''

global ITEM_MUNKI_INSTALLS_ARRAY
ITEM_MUNKI_INSTALLS_ARRAY = []
ITEM_MUNKI_INSTALLS_ITEM = {}
ITEM_MUNKI_INSTALLS_ITEM['type'] = "application"
ITEM_MUNKI_INSTALLS_ITEM['path'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['CFBundleVersion'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['version_comparison_key'] = "CFBundleVersion"
ITEM_MUNKI_INSTALLS_ARRAY.append(ITEM_MUNKI_INSTALLS_ITEM)

def create_pkginfo(given_app_version,given_app_munki_installs_path,given_repo_path_to_pkg,given_app_serial,given_app_prod_key,given_app_license_server,given_installer_choices_key):
    '''Makes the pkginfo for this item.'''
    
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path
    
    preinstall_script_content = ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE.replace("__%app_serial%__",given_app_serial).replace("__%app_prod_key%__",given_app_prod_key).replace("__%app_license_server%__",given_app_license_server)


    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % ITEM_MUNKI_NAME,
                                          '--catalog=%s' % ITEM_MUNKI_CATALOG_NAME,
                                          '--description=%s' % ITEM_MUNKI_DESCRIPTION,
                                          '--developer=%s' % ITEM_MUNKI_DEVELOPER_NAME,
                                          '--category=%s' % ITEM_MUNKI_CATEGORY,
                                          '--unattended_install',
                                          '--pkgvers=%s' % given_app_version,
                                          '--displayname=%s' % ITEM_MUNKI_DISP_NAME,
                                          munki_repo_pkg_path])
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
        output_dict['preinstall_script'] = preinstall_script_content
    except NameError:
        pass
    try:
        output_dict['installer_choices_xml'] = given_installer_choices_key
    except NameError:
        pass
    try:
        output_dict['installs'] = ITEM_MUNKI_INSTALLS_ARRAY
    except NameError:
        pass
    try:
        output_dict['installs'][0]['CFBundleVersion'] = given_app_version
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
    app_version = raw_input("AutoCAD version: ")
    app_munki_installs_path = raw_input("Path where app is installed (relative to client): ")
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)
    app_serial = raw_input("AutoCAD Serial (looks like 123-44455678): ")
    app_prod_key = raw_input("AutoCAD Product Key (looks like 1234A5): ")
    app_license_server = raw_input("AutoCAD license server hostname: ")
    choice_changes_xml_path = raw_input("Path to the Installer Choice Changes XML: ")
    try:
        installer_choices_dict = plistlib.readPlist(choice_changes_xml_path)
    except xml.parsers.expat.ExpatError:
        print "Invalid choice changes file."
        sys.exit(1)
    try:
        installer_choices_key = installer_choices_dict['installer_choices_xml']
    except KeyError:
        print "Invalid installer_choices_xml key."
        sys.exit(1)
    # Generate pkginfo:
    if not create_pkginfo(app_version,app_munki_installs_path,repo_path_to_pkg,app_serial,app_prod_key,app_license_server,installer_choices_key):
        print "Failed create pkginfo."
        sys.exit(1)
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
