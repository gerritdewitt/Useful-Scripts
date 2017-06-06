#!/usr/bin/env python

# make-pkginfo.py
# Script for programmatically generating pkginfo for various
# Microsoft Office 2011/2016 updates and standalone apps.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28, 2015-09-11, 2015-11-17, 2015-11-23 (Apple HW Bundle),
# 2016-01-11, 2016-10-17, 2017-01-03, 2017-04-11, 2017-06-06.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys, datetime, shutil, uuid

def inspect_dmg_silverlight(given_repo_path_to_pkg):
    '''Looks inside a dmg with a Silverlight installer to gather version.'''
    print "Inspecting dmg..."
    # Default:
    dmg_contents = []
    silverlight_outer_pkg_basename = ''
    expanded_outer_pkg_contents = []
    silverlight_inner_pkg_basename = ''
    silverlight_inner_pkg_info_plist_path = ''
    pkg_info_plist_lines = []
    silverlight_vers = ''
    # Paths:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    if not os.path.exists(munki_repo_pkg_path):
        print "Not found in repo: %s" % munki_repo_pkg_path
        return '',''
    tmp_dmg_path = os.path.join("/private/tmp","%s.dmg" % uuid.uuid4())
    tmp_dmg_mp_path = os.path.join("/private/tmp","%s.mount-point" % uuid.uuid4())
    # Copy dmg:
    shutil.copyfile(munki_repo_pkg_path,tmp_dmg_path)
    # Mount dmg:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'attach',
                               '-mountpoint',
                               tmp_dmg_mp_path,
                               tmp_dmg_path])
        did_mount_dmg = True
        print "Silverlight: Mounted copy of dmg to %s." % tmp_dmg_mp_path
    except subprocess.CalledProcessError:
        did_mount_dmg = False
    # List mounted dmg contents:
    if did_mount_dmg:
        dmg_contents = os.listdir(tmp_dmg_mp_path)
        # Inspect contents of dmg; get outer pkg path:
        for i in dmg_contents:
            if i.endswith('.pkg'):
                silverlight_outer_pkg_basename = i
                break
    # Expand outer pkg:
    if silverlight_outer_pkg_basename:
        silverlight_outer_pkg_path = os.path.join(tmp_dmg_mp_path,silverlight_outer_pkg_basename)
        print "Silverlight: Outer pkg path is %s." % silverlight_outer_pkg_path
        silverlight_outer_pkg_expanded_path = os.path.join("/private/tmp","%s.dir" % uuid.uuid4())
        try:
            subprocess.check_call(['/usr/sbin/pkgutil',
                                   '--expand',
                                   silverlight_outer_pkg_path,
                                   silverlight_outer_pkg_expanded_path])
            did_expand_pkg = True
            print "Silverlight: Expanded outer pkg to %s." % silverlight_outer_pkg_expanded_path
        except subprocess.CalledProcessError:
            did_expand_pkg = False
    # List expanded outer pkg contents:
    if did_expand_pkg:
        expanded_outer_pkg_contents = os.listdir(silverlight_outer_pkg_expanded_path)
        # Inspect contents of expanded outer pkg; get inner component pkg:
        for i in expanded_outer_pkg_contents:
            if i.endswith('.pkg') and i.startswith('silverlight'):
                silverlight_inner_pkg_basename = i
                break
    # Get details from inner pkg:
    if silverlight_inner_pkg_basename:
        silverlight_inner_pkg_path = os.path.join(silverlight_outer_pkg_expanded_path,silverlight_inner_pkg_basename)
        print "Silverlight: Inner pkg path is %s." % silverlight_inner_pkg_path
        silverlight_inner_pkg_info_plist_path = os.path.join(silverlight_inner_pkg_path,'PackageInfo')
        print "Silverlight: Inner pkg info is %s." % silverlight_inner_pkg_info_plist_path
    # Get version and installed path from PackageInfo:
    if os.path.exists(silverlight_inner_pkg_info_plist_path):
        try:
            file_handle = open(silverlight_inner_pkg_info_plist_path,'r')
            silverlight_inner_pkg_info_plist_content = file_handle.read()
            file_handle.close()
            pkg_info_plist_lines = silverlight_inner_pkg_info_plist_content.split('\n')
        except IOError:
            pass
    for line in pkg_info_plist_lines:
        if 'com.microsoft.SilverlightPlugin' in line and 'CFBundleShortVersionString' in line:
            line = line.replace('"','').replace('<','').replace('>','')
            line_attrs = line.split(' ')
            for attr in line_attrs:
                if 'CFBundleShortVersionString' in attr:
                    silverlight_vers = attr.replace('CFBundleShortVersionString','').replace('=','').strip()
                    print "Silverlight: Version from PackageInfo is %s." % silverlight_vers
                    break
        if silverlight_vers:
            break
    # Unmount dmg:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'eject',
                               tmp_dmg_mp_path])
    except subprocess.CalledProcessError:
        pass
    # Remove copied dmg and expanded outer pkg:
    if os.path.exists(tmp_dmg_path):
        try:
            os.unlink(tmp_dmg_path)
        except OSError:
            pass
    if os.path.exists(silverlight_outer_pkg_expanded_path):
        try:
            shutil.rmtree(silverlight_outer_pkg_expanded_path)
        except OSError:
            pass
    # Return:
    return silverlight_vers

def create_pkginfo(given_item_munki_name,given_item_munki_display_name,given_item_munki_description,given_app_version,given_min_macos_version,given_item_munki_installs_paths,given_due_date_interval_days,given_repo_path_to_pkg,given_item_munki_update_for):
    '''Writes the pkginfo.'''
    # Set up names and paths:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,'%(name)s-%(vers)s' % {"name":given_item_munki_name,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % given_item_munki_name,
                                          '--displayname=%s' % given_item_munki_display_name,
                                          '--description=%s' % given_item_munki_description,
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
        # Add an "installs" array: this is the magic that makes Microsoft Office
        # updates work with munki.  Recall the "installs" array overrides pkg receipts
        # and that pkg receipts for Office apps are not reliable.
        # For the Office 2011 case, we will have an array (all apps are versioned as a suite).
        # For other cases, we will have a one-element array.
        output_dict['installs'] = []
        for app_path in given_item_munki_installs_paths:
            installs_dict = {}
            installs_dict['type'] = 'application'
            installs_dict['path'] = app_path
            installs_dict['CFBundleShortVersionString'] = given_app_version
            output_dict['installs'].append(installs_dict)
        # Add "update_for" if this is an update:
        if given_item_munki_update_for:
            output_dict['update_for'] = [given_item_munki_update_for]
        # Add due date if specified:
        if given_due_date_interval_days >=0:
            now = datetime.datetime.utcnow()
            delta = datetime.timedelta(int(given_due_date_interval_days))
            output_dict['force_install_after_date'] = (now + delta)


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

    # General variables; edit to suit your needs:
    global ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY
    ITEM_MUNKI_CATALOG_NAME = "software"
    ITEM_MUNKI_DEVELOPER_NAME = "Microsoft"
    ITEM_MUNKI_CATEGORY = "Microsoft"
    
    # Gather item info:
    print '''
Is this Microsoft item one of the following?
   - An update to an Office 2016 app? If so, type "2016" and press return.
   - An update to an Office 2011 suite? If so, type "2011" and press return.
   - An update to Microsoft AutoUpdate?  If so, type "mau" and press return.
   - An update to the Silverlight plug-in?  If so, type "silverlight" and press return.
   - A standalone product? If so, type "standalone" and press return.
    '''
    ms_type = raw_input("Type of updater or standalone item: ").replace(' ','').replace('\n','').lower()
    if not ms_type or (ms_type and ms_type not in ["2016","2011","mau","silverlight","standalone"]):
        print "Please retry, specifying update type (2016, 2011), mau, silverlight, or standalone."
        sys.exit(1)

    # Path to "pkg" (dmg).  We need this first to measure version, etc.
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)

    if ms_type == "2016":
        print "Adding an update for an Office 2016 app..."
        item_munki_update_for = "Microsoft_Office_2016"
        app_name = raw_input("Name of the Office 2016 app: ")
        item_munki_name = "Microsoft_Office_2016_%s_Update" % app_name
        item_munki_display_name = "Microsoft Office 2016 %s Update" % app_name
        app_version = raw_input("App (package) version: ")
        item_munki_description = item_munki_display_name
        min_macos_version = "10.10"
        item_munki_installs_paths = []
        item_munki_installs_paths.append("/Applications/Microsoft %s.app" % app_name)
    elif ms_type == "2011":
        print "Adding an update for the Office 2011 suite..."
        item_munki_update_for = "Microsoft_Office_2011"
        item_munki_name = "Microsoft_Office_2011_Update"
        item_munki_display_name = "Microsoft Office 2011 Update"
        app_version = raw_input("Office 2011 (package) version: ")
        item_munki_description = item_munki_display_name
        min_macos_version = "10.9"
        item_munki_installs_paths = []
        for app_name in ['Word','Excel','PowerPoint','Outlook']:
            item_munki_installs_paths.append("/Applications/Microsoft Office 2011/Microsoft %s.app" % app_name)
    elif ms_type == "mau":
        print "Adding Microsoft AutoUpdate..."
        item_munki_update_for = "Microsoft_Office_2016"
        item_munki_name = "Microsoft_AutoUpdate"
        item_munki_display_name = "Microsoft Office AutoUpdate App"
        app_version = raw_input("App (package) version: ")
        item_munki_description = item_munki_display_name
        min_macos_version = "10.9"
        item_munki_installs_paths = []
        item_munki_installs_paths.append("/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app")
    elif ms_type == "silverlight":
        print "Adding Microsoft Silverlight..."
        item_munki_update_for = ""
        item_munki_name = "Microsoft_Silverlight"
        item_munki_display_name = "Microsoft Silverlight Plug-in"
        app_version = inspect_dmg_silverlight(repo_path_to_pkg)
        item_munki_description = item_munki_display_name
        min_macos_version = "10.9"
        item_munki_installs_paths = []
        item_munki_installs_paths.append("/Library/Internet Plug-Ins/Silverlight.plugin")
    elif ms_type == "standalone":
        print "Adding a standalone Microsoft app..."
        item_munki_update_for = ""
        item_munki_name = raw_input("Package name (per our conventions): ")
        item_munki_display_name = raw_input("Package display name: ")
        app_version = raw_input("App (package) version: ")
        item_munki_description = item_munki_display_name
        min_macos_version = raw_input("Minimal macOS version required for this app: ")
        app_installed_path = raw_input("Path where app is installed (relative to client): ").replace("\\","")
        item_munki_installs_paths = []
        item_munki_installs_paths.append(app_installed_path)

    # Optional due date:
    due_date_interval_days = raw_input("Update due date in days (press return to skip): ").replace(' ','').replace('\n','')
    if not due_date_interval_days:
        due_date_interval_days = -1
    # Create pkginfo:
    if not create_pkginfo(item_munki_name,item_munki_display_name,item_munki_description,app_version,min_macos_version,item_munki_installs_paths,due_date_interval_days,repo_path_to_pkg,item_munki_update_for):
        print "Error creating pkginfo!"

if __name__ == "__main__":
    main()
