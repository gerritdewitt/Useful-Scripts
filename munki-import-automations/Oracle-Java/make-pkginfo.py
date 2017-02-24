#!/usr/bin/env python

# make-pkginfo.py
# Script for programmatically generating pkginfo for various
# Oracle Java products (JRE, JDK).
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28, 2015-09-11, 2015-11-17, 2015-11-23 (Apple HW Bundle),
# 2016-01-11, 2016-10-17, 2017-01-03.
# 2017-02-17, 2017-02-24.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys, datetime, shutil, uuid

def inspect_dmg_jdk(given_repo_path_to_pkg):
    '''Looks inside a dmg with an Oracle JDK installer to gather some data about the contents.
        Measures version for JDK and determines the final installed path.'''
    print "Inspecting dmg..."
    # Default:
    dmg_contents = []
    oracle_outer_pkg_basename = ''
    expanded_outer_pkg_contents = []
    oracle_inner_pkg_basename = ''
    oracle_inner_pkg_info_plist_path = ''
    oracle_inner_pkg_info_plist_lines = []
    oracle_vers = ''
    oracle_installed_path = ''
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
        print "Oracle JDK: Mounted copy of dmg to %s." % tmp_dmg_mp_path
    except subprocess.CalledProcessError:
        did_mount_dmg = False
    # List mounted dmg contents:
    if did_mount_dmg:
        dmg_contents = os.listdir(tmp_dmg_mp_path)
    # Inspect contents of dmg; get outer pkg path:
    for i in dmg_contents:
        if i.endswith('.pkg'):
            oracle_outer_pkg_basename = i
            break
    # Expand outer pkg:
    if oracle_outer_pkg_basename:
        oracle_outer_pkg_path = os.path.join(tmp_dmg_mp_path,oracle_outer_pkg_basename)
        print "Oracle JDK: Outer pkg path is %s." % oracle_outer_pkg_path
        oracle_outer_pkg_expanded_path = os.path.join("/private/tmp","%s.dir" % uuid.uuid4())
        try:
            subprocess.check_call(['/usr/sbin/pkgutil',
                                   '--expand',
                                   oracle_outer_pkg_path,
                                   oracle_outer_pkg_expanded_path])
            did_expand_pkg = True
            print "Oracle JDK: Expanded outer pkg to %s." % oracle_outer_pkg_expanded_path
        except subprocess.CalledProcessError:
            did_expand_pkg = False
    # List expanded outer pkg contents:
    if did_expand_pkg:
        expanded_outer_pkg_contents = os.listdir(oracle_outer_pkg_expanded_path)
    # Inspect contents of expanded outer pkg; get inner component pkg:
    for i in expanded_outer_pkg_contents:
        if i.endswith('.pkg') and i.startswith('jdk'):
            oracle_inner_pkg_basename = i
            break
    # Get details from inner pkg:
    if oracle_inner_pkg_basename:
        oracle_inner_pkg_path = os.path.join(oracle_outer_pkg_expanded_path,oracle_inner_pkg_basename)
        print "Oracle JDK: Inner pkg path is %s." % oracle_inner_pkg_path
        oracle_inner_pkg_info_plist_path = os.path.join(oracle_inner_pkg_path,'PackageInfo')
        print "Oracle JDK: Inner pkg info is %s." % oracle_inner_pkg_info_plist_path
    # Get version and installed path from PackageInfo:
    if os.path.exists(oracle_inner_pkg_info_plist_path):
        try:
            oracle_inner_pkg_info_plist_handle = open(oracle_inner_pkg_info_plist_path,'r')
            oracle_inner_pkg_info_plist_content = oracle_inner_pkg_info_plist_handle.read()
            oracle_inner_pkg_info_plist_handle.close()
            oracle_inner_pkg_info_plist_lines = oracle_inner_pkg_info_plist_content.split('\n')
        except IOError:
            pass
    for line in oracle_inner_pkg_info_plist_lines:
        if 'CFBundleVersion' in line:
            line = line.replace('"','').replace('<','').replace('>','')
            line_attrs = line.split(' ')
            for attr in line_attrs:
                if 'CFBundleVersion' in attr:
                    oracle_vers = attr.replace('CFBundleVersion','').replace('=','').replace(' ','')
                    print "Oracle JDK: Version from PackageInfo is %s." % oracle_vers
                    break
        if 'install-location' in line:
            line = line.replace('"','').replace('<','').replace('>','')
            line_attrs = line.split(' ')
            for attr in line_attrs:
                if 'install-location' in attr:
                    oracle_installed_path = attr.replace('install-location','').replace('=','')
                    print "Oracle JDK: Installed path from PackageInfo is %s." % oracle_installed_path
                    break
        if oracle_vers and oracle_installed_path:
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
    if os.path.exists(oracle_outer_pkg_expanded_path):
        try:
            shutil.rmtree(oracle_outer_pkg_expanded_path)
        except OSError:
            pass
    # Return:
    return oracle_vers,oracle_installed_path

def inspect_dmg_jre(given_repo_path_to_pkg):
    '''Looks inside a dmg with an Oracle JRE installer to gather some data about the contents.
        Returns version for JRE and the basename of the installer app (in the dmg) that contains the pkg.'''
    print "Inspecting dmg..."
    # Default:
    dmg_contents = []
    oracle_installer_app_basename = ''
    oracle_installer_app_info_plist_path = ''
    oracle_vers = ''
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
        print "Oracle JRE: Mounted copy of dmg to %s." % tmp_dmg_mp_path
        did_mount_dmg = True
    except subprocess.CalledProcessError:
        did_mount_dmg = False
    # List mounted dmg contents:
    if did_mount_dmg:
        dmg_contents = os.listdir(tmp_dmg_mp_path)
    # Inspect contents:
    for i in dmg_contents:
        if i.endswith('.app'):
            oracle_installer_app_basename = i
            break
    # Get path to Info.plist:
    if oracle_installer_app_basename:
        print "Oracle JRE: Installer app basename is %s." % oracle_installer_app_basename
        oracle_installer_app_path = os.path.join(tmp_dmg_mp_path,oracle_installer_app_basename)
        print "Oracle JRE: Installer app path is %s." % oracle_installer_app_path
        oracle_installer_app_info_plist_path = os.path.join(oracle_installer_app_path,'Contents/Info.plist')
        print "Oracle JRE: Installer app info is %s." % oracle_installer_app_info_plist_path
    # Get version from Info.plist:
    if os.path.exists(oracle_installer_app_info_plist_path):
        try:
            oracle_installer_app_info_dict = plistlib.readPlist(oracle_installer_app_info_plist_path)
        except xml.parsers.expat.ExpatError:
            oracle_installer_app_info_dict = {}
        try:
            oracle_vers = oracle_installer_app_info_dict['CFBundleVersion']
            print "Oracle JRE: Version from installer app info is %s." % oracle_vers
        except KeyError:
            pass
    # Unmount dmg:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                           'eject',
                           tmp_dmg_mp_path])
    except subprocess.CalledProcessError:
        pass
    # Remove copied dmg:
    if os.path.exists(tmp_dmg_path):
        try:
            os.unlink(tmp_dmg_path)
        except OSError:
            pass
    # Return:
    return oracle_vers,oracle_installer_app_basename

def create_pkginfo(given_due_date_interval_days,given_repo_path_to_pkg):
    '''Writes the pkginfo.'''
    # Set up names and paths:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,given_repo_path_to_pkg)
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,'%(name)s-%(vers)s' % {"name":ITEM_MUNKI_NAME,"vers":ITEM_MUNKI_VERSION})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path

    # Installcheck script content, if specified:
    if ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH:
        h = open(ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH,'r')
        installcheck_script_content = h.read()
        h.close()
        installcheck_script_content = installcheck_script_content.replace("__%jdk_version%__",ITEM_MUNKI_VERSION)
        item_munki_installcheck_path = "/private/tmp/%s_installcheck_script.py" % ITEM_MUNKI_NAME
        h = open(item_munki_installcheck_path,'w')
        h.write(installcheck_script_content)
        h.close()

    # Assemble makepkginfo cmd:
    cmd = ['/usr/local/munki/makepkginfo',
           '--name=%s' % ITEM_MUNKI_NAME,
           '--displayname=%s' % ITEM_MUNKI_DISP_NAME,
           '--description=%s' % ITEM_MUNKI_DESCRIPTION,
           '--catalog=%s' % ITEM_MUNKI_CATALOG_NAME,
           '--developer=%s' % ITEM_MUNKI_DEVELOPER_NAME,
           '--unattended_install',
           '--pkgvers=%s' % ITEM_MUNKI_VERSION]
   # Add installcheck script (JDK case):
    if ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH:
        cmd.append('--installcheck_script=%s' % item_munki_installcheck_path)
   # Add package_path (JRE case):
    if ITEM_MUNKI_PKG_PATH_IN_DMG:
        cmd.append('--pkgname=%s' % ITEM_MUNKI_PKG_PATH_IN_DMG)
    cmd.append(munki_repo_pkg_path)
    # Call makepkginfo:
    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        return False
    try:
        output_dict = plistlib.readPlistFromString(output)
    except xml.parsers.expat.ExpatError:
        return False
    # Add items that makepkginfo did not:
    if output_dict:
        output_dict['category'] = ITEM_MUNKI_CATEGORY
        output_dict['minimum_os_version'] = ITEM_MUNKI_MIN_OS
        # Add an "installs" array with the installs dict, if specified:
        if ITEM_MUNKI_INSTALLS_DICT:
            output_dict['installs'] = [ITEM_MUNKI_INSTALLS_DICT] # JRE only
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

    global THIS_DIR
    THIS_DIR = os.path.dirname(os.path.realpath(__file__))
    # General variables; edit to suit your needs:
    global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_DESCRIPTION, ITEM_MUNKI_VERSION
    global ITEM_MUNKI_INSTALLS_DICT, ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH, ITEM_MUNKI_PKG_PATH_IN_DMG
    global ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY
    ITEM_MUNKI_CATALOG_NAME = "software"
    ITEM_MUNKI_DEVELOPER_NAME = "Oracle"
    ITEM_MUNKI_CATEGORY = "Oracle"

    # Gather item info:
    print '''
Is this Oracle item one of the following?
    - A JRE and browser plugin? If so, type "jre" and press return.
    - A JDK? If so, type "jdk" and press return.
    '''
    oracle_type = raw_input("Type of Oracle item: ").replace(' ','').replace('\n','').lower()
    if not oracle_type or (oracle_type and oracle_type not in ["jre","jdk"]):
        print "Please retry, specifying a type (jre, jdk)."
        sys.exit(1)
    
    # Path to "pkg" (dmg).  We need this first to measure version, etc.
    repo_path_to_pkg = raw_input("Path to the item in repo (relative to %s): " % MUNKI_PKGS_PATH)

    if oracle_type == "jre":
        print "Adding an Oracle JRE with browser plugin..."
        ITEM_MUNKI_VERSION, jre_installer_app_basename = inspect_dmg_jre(repo_path_to_pkg)
        ITEM_MUNKI_NAME = "Oracle_Java_Plugin"
        ITEM_MUNKI_DISP_NAME = "Oracle Java Plugin"
        ITEM_MUNKI_DESCRIPTION = "Java Runtime (JRE) and browser plugin"
        ITEM_MUNKI_MIN_OS = raw_input("Minimal macOS version required: ")
        ITEM_MUNKI_INSTALLS_DICT = {}
        ITEM_MUNKI_INSTALLS_DICT['type'] = 'bundle'
        ITEM_MUNKI_INSTALLS_DICT['path'] = "/Library/Internet Plug-Ins/JavaAppletPlugin.plugin"
        ITEM_MUNKI_INSTALLS_DICT['CFBundleVersion'] = ITEM_MUNKI_VERSION
        ITEM_MUNKI_INSTALLS_DICT['version_comparison_key'] = 'CFBundleVersion'
        ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH = '' # JRE uses installs array, so no need
        ITEM_MUNKI_PKG_PATH_IN_DMG = "%s/Contents/Resources/JavaAppletPlugin.pkg" % jre_installer_app_basename

    elif oracle_type == "jdk":
        print "Adding an Oracle JDK..."
        ITEM_MUNKI_VERSION, jdk_installed_path = inspect_dmg_jdk(repo_path_to_pkg)
        ITEM_MUNKI_NAME = "Oracle_Java_JDK"
        ITEM_MUNKI_DISP_NAME = "Oracle Java JDK"
        ITEM_MUNKI_DESCRIPTION = "Java Development Kit (JDK) with Runtime (JRE)"
        ITEM_MUNKI_MIN_OS = raw_input("Minimal macOS version required: ")
        ITEM_MUNKI_INSTALLS_DICT = {} # JDK uses an installcheck script, so no need
        ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH = os.path.join(THIS_DIR, "jdk-installcheck-template.py")
        ITEM_MUNKI_PKG_PATH_IN_DMG = '' # JDK pkg at root of dmg, so no need

    # Common to all:
    due_date_interval_days = raw_input("Update due date in days (press return to skip): ").replace(' ','').replace('\n','')
    if not due_date_interval_days:
        due_date_interval_days = -1
    # Create pkginfo:
    if not create_pkginfo(due_date_interval_days,repo_path_to_pkg):
        print "Error creating pkginfo!"

if __name__ == "__main__":
    main()
