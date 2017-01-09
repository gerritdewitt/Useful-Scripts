#!/usr/bin/env python

# make-pkginfo.py
# Script for generating pkginfo for deploying MathWorks MATLAB via Munki.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24/28, 2015-09-11 (config profile and pkginfo creation), 2015-09-15, 2015-09-30 (first pass at Matlab postinstall scripts)
# 2015-11-24 (conditions), 2015-11-25, 2015-12-07, 2016-03-21 (EndNote), 2016-07-28, 2016-08-30, 2016-10-03, 2016-11-09, 2016-11-14
# 2016-11-29 (Autodesk), 2016-12-07, 2016-12-09, 2016-12-12 (SPSS), 2017-01-05/09.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys

# Script templates:
# These are likely to require adjustment for each major MATLAB version.
global ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE
ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE = '''#!/bin/bash
installer_bin="/private/tmp/InstallForMacOSX.app/Contents/MacOS/InstallForMacOSX"

# Files used by installer:
installer_input_file_path="/private/tmp/matlab_installer_input.txt"
installer_output_file_path="/private/tmp/matlab_installer_output.txt"
network_license_path="/private/tmp/matlab_network.lic"
activation_file_path="/private/tmp/matlab_activation.ini"

# File contents:
installer_input_content="fileInstallationKey=__%app_file_installation_key%__
agreeToLicense=yes
outputFile=$installer_output_file_path
mode=silent
activationPropertiesFile=$activation_file_path
licensePath=$network_license_path
"

network_license_content="__%app_license_string%__
USE_SERVER
"

activation_ini_content="isSilent=True
activateCommand=activateOffline
licensePath=$network_license_path
licenseFile=$network_license_path
"

# Write files used by installer:
/bin/echo "$installer_input_content" > "$installer_input_file_path"
/bin/echo "$network_license_content" > "$network_license_path"
/bin/echo "$activation_ini_content" > "$activation_file_path"

# Call vendor installer:
"$installer_bin" -inputFile "$installer_input_file_path"

# Clean up:
if [ -f "$installer_bin" ]; then
    /bin/rm "$installer_bin"
fi
if [ -f "$installer_input_file_path" ]; then
    /bin/rm "$installer_input_file_path"
fi
if [ -f "$network_license_path" ]; then
    /bin/rm "$network_license_path"
fi
if [ -f "$activation_file_path" ]; then
    /bin/rm "$activation_file_path"
fi
'''
global ITEM_MUNKI_UNINSTALL_SCRIPT_CONTENT_TEMPLATE
ITEM_MUNKI_UNINSTALL_SCRIPT_CONTENT_TEMPLATE = '''#!/bin/bash
app_path="__%app_munki_installs_path%__"
if [ -d "$app_path" ]; then
    /bin/rm -fr "$app_path"
fi
'''

global ITEMS_TO_COPY
ITEMS_TO_COPY = []
COPY_ITEM = {'destination_path':"/private/tmp",
'source_item':"replaced by create_pkginfo()",
'destination_item':"InstallForMacOSX.app"}
ITEMS_TO_COPY.append(COPY_ITEM)

global ITEM_MUNKI_INSTALLS_ARRAY
ITEM_MUNKI_INSTALLS_ARRAY = []
ITEM_MUNKI_INSTALLS_ITEM = {}
ITEM_MUNKI_INSTALLS_ITEM['type'] = "application"
ITEM_MUNKI_INSTALLS_ITEM['path'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['CFBundleVersion'] = "replaced by create_pkginfo()"
ITEM_MUNKI_INSTALLS_ITEM['version_comparison_key'] = "CFBundleVersion"
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

def create_pkginfo(given_app_version,given_app_munki_installs_path,given_repo_path_to_pkg,given_app_file_installation_key,given_app_license_string):
    '''Makes the pkginfo for this item.'''
    # Paths:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path
    # Postinstall script content:
    postinstall_script_content = ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE.replace("__%app_license_string%__",given_app_license_string).replace("__%app_file_installation_key%__",given_app_file_installation_key)
    # Uninstall script content:
    uninstall_script_content = ITEM_MUNKI_UNINSTALL_SCRIPT_CONTENT_TEMPLATE.replace("__%app_munki_installs_path%__",given_app_munki_installs_path)
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
    # Update source item for "items to copy":
    ITEMS_TO_COPY[0]['source_item'] = ITEMS_TO_COPY_SRC_ITEM
    # Make "items to copy" arg string:
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
        output_dict['installs'][0]['CFBundleVersion'] = given_app_version
        output_dict['installs'][0]['path'] = given_app_munki_installs_path
    except KeyError, IndexError:
        pass
    # Uninstall method:
    output_dict['uninstall_method'] = "uninstall_script"
    try:
        output_dict['uninstall_script'] = uninstall_script_content
    except NameError:
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

    # General variables; edit to suit your needs:
    global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DESCRIPTION, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY, ITEM_MUNKI_POSTINSTALL_SCRIPT_CONTENT_TEMPLATE
    ITEM_MUNKI_NAME = "MathWorks_MATLAB"
    ITEM_MUNKI_DISP_NAME = "MathWorks MATLAB"
    ITEM_MUNKI_MIN_OS = "10.10.5"
    ITEM_MUNKI_CATALOG_NAME = "software"
    ITEM_MUNKI_DEVELOPER_NAME = "MathWorks"
    ITEM_MUNKI_CATEGORY = "Math & Statistics"
    ITEM_MUNKI_DESCRIPTION = "Installs MathWorks MATLAB configured to use the license server."
    global ITEMS_TO_COPY_SRC_ITEM
    ITEMS_TO_COPY_SRC_ITEM = "InstallForMacOSX.app"

    # Gather item info:
    app_version = raw_input("MATLAB version: ")
    app_munki_installs_path = raw_input("Path where app is installed (relative to client, should start with /Applications): ")
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)
    print '''
MATLAB File Installation Key:
   - This is a string of 12 groups of 5 numbers separated by dashes.
   - Example: 11111-22222-33333-44444-55555-66666-77777-88888-99999-00000-11111-22222
'''
    app_file_installation_key = raw_input("MATLAB File Installation Key: ")
    print '''
License File String:
   - This includes the host name of the license server with some extra details.
   - Example: SERVER server.host.name AABB11223344 27000
'''
    app_license_string = raw_input("License File String: ")

    # Generate pkginfo:
    if not create_pkginfo(app_version,app_munki_installs_path,repo_path_to_pkg,app_file_installation_key,app_license_string):
        print "Failed to create pkginfo."
        sys.exit(1)
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
