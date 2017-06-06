#!/usr/bin/env python

# make-pkginfo.py
# Script for programmatically generating pkginfo for an App Store app
# that may be delivered via hardware bundle license or volume license purchase.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28, 2015-09-11, 2015-11-17, 2015-11-23, 2016-02-08, 2016-10-13, 2016-11-14, 2016-11-29, 2016-12-05.
# 2017-04-18, 2017-06-06.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys

# General variables; edit to suit your needs:
global  ITEM_MUNKI_CATALOG_NAME
ITEM_MUNKI_CATALOG_NAME = "software" # catalog to which this item will be published
global ITEM_MUNKI_CATEGORY, ITEM_MUNKI_DEVELOPER_NAME
ITEM_MUNKI_CATEGORY = "Apple"
ITEM_MUNKI_DEVELOPER_NAME = "Apple"
global ITEM_MUNKI_HW_BUNDLE_DESCRIPTION, ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE
ITEM_MUNKI_HW_BUNDLE_DESCRIPTION = "__%APP%__ is available to Mac systems with a hardware bundle license for it.  Generally, this should be all Mac computers shipping on or after its release on October 23, 2013.  It may also be deployed to systems for which a VPP license was purchased."
ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE = '''#!/bin/bash
suffix="$(/bin/date +%h%m%s)"
lsregister="/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister"
if [ -d "__%APP_PATH%__" ]; then
   mv "__%APP_PATH%__" "/private/tmp/__%APP%__-${suffix}"
   "$lsregister" -kill -r -domain local -domain user
fi
'''

global ITEM_MUNKI_INSTALLS_ARRAY
ITEM_MUNKI_INSTALLS_ARRAY = []
ITEM_MUNKI_INSTALLS_ITEM = {}
ITEM_MUNKI_INSTALLS_ITEM['type'] = "application"
ITEM_MUNKI_INSTALLS_ITEM['path'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['CFBundleShortVersionString'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ARRAY.append(ITEM_MUNKI_INSTALLS_ITEM)

def create_pkginfo(given_app_munki_pkg_name,given_app_munki_pkg_display_name,given_app_version,given_min_macos_version,given_app_munki_installs_path,given_repo_path_to_pkg):
    '''Makes the pkginfo for this item.'''

    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)

    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,'%(name)s-%(vers)s' % {"name":given_app_munki_pkg_name,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path

    # Create a nice description for HW Bundle Apps:
    app_munki_pkg_description = given_app_munki_pkg_display_name # default
    for hw_bundle_app_name in ['iMovie','GarageBand','Pages','Numbers','Keynote']:
        if given_app_munki_pkg_name.lower().find(hw_bundle_app_name.lower()) != -1:
            app_munki_pkg_description = ITEM_MUNKI_HW_BUNDLE_DESCRIPTION.replace("__%APP%__",given_app_munki_pkg_display_name)
            break
    # Create a preinstall script for removing the app:
    # App Store "updates" are full app replacements:
    preinstall_script_content = ITEM_MUNKI_PREINSTALL_SCRIPT_CONTENT_TEMPLATE.replace("__%APP_PATH%__",given_app_munki_installs_path).replace("__%APP%__",given_app_munki_pkg_name)

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % given_app_munki_pkg_name,
                                          '--displayname=%s' % given_app_munki_pkg_display_name,
                                          '--description=%s' % app_munki_pkg_description,
                                          '--catalog=%s' % ITEM_MUNKI_CATALOG_NAME,
                                          '--developer=%s' % ITEM_MUNKI_DEVELOPER_NAME,
                                          '--unattended_install',
                                          '--pkgvers=%s' % given_app_version,
                                          munki_repo_pkg_path])
    except subprocess.CalledProcessError:
        return False
    try:
        output_dict = plistlib.readPlistFromString(output)
    except xml.parsers.expat.ExpatError:
        return False
    # Add items that makepkginfo did not:
    if output_dict:
        output_dict['category'] = ITEM_MUNKI_CATEGORY
        output_dict['minimum_os_version'] = given_min_macos_version
        output_dict['preinstall_script'] = preinstall_script_content
        output_dict['installs'] = ITEM_MUNKI_INSTALLS_ARRAY
        output_dict['installs'][0]['CFBundleShortVersionString'] = given_app_version
        output_dict['installs'][0]['path'] = given_app_munki_installs_path

    # Write pkginfo:
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
    app_munki_pkg_name = raw_input("Package name (per our conventions): ")
    app_munki_pkg_display_name = raw_input("Package display name: ")
    app_version = raw_input("App (package) version: ")
    min_macos_version = raw_input("Minimal macOS version required for this app: ")
    app_munki_installs_path = raw_input("Path where app is installed (relative to client): ").replace("\\","")
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)
    # Generate pkginfo:
    if not create_pkginfo(app_munki_pkg_name,app_munki_pkg_display_name,app_version,min_macos_version,app_munki_installs_path,repo_path_to_pkg):
        print "Error creating pkginfo!"
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
