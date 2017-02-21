#!/usr/bin/env python

# make-mobileconfig-and-pkginfo.py
# Script for creating a "nopkg" Munki item that
# sets permissions on Managed Software Center so
# that only admin users can open and use it.
# This has a side effect of suppressing MSC
# notifications for non-admin users, too.
# Documentation & References: See closest ReadMe.


# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-24/28.
# 2016-10-24, 2016-12-02 (config profiles)
# 2017-01-25, 2017-01-30, 2017-02-16.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, plistlib, subprocess

def write_pkginfo_and_add_to_repo():
    '''Writes the pkginfo for the nopkg item to the Munki repository.'''
    
    this_dir = os.path.dirname(os.path.realpath(__file__))
    print "Working dir is %s." % this_dir
    pkginfo_file_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name":ITEM_MUNKI_NAME, "vers": ITEM_MUNKI_VERSION})
    print "Pkginfo will be %s." % pkginfo_file_path

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % ITEM_MUNKI_NAME,
                                          '--pkgvers=%s' % ITEM_MUNKI_VERSION,
                                          '--catalog=configuration',
                                          '--nopkg',
                                          '--unattended_install',
                                          '--unattended_uninstall',
                                          '--uninstallcheck_script=%s' % ITEM_MUNKI_UNINSTALLCHECK_SCRIPT,
                                          '--uninstall_script=%s' % ITEM_MUNKI_UNINSTALL_SCRIPT,
                                          '--installcheck_script=%s' % ITEM_MUNKI_INSTALLCHECK_SCRIPT,
                                          '--preinstall_script=%s' % ITEM_MUNKI_PREINSTALL_SCRIPT])
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
    global ITEM_MUNKI_NAME, ITEM_MUNKI_VERSION
    global ITEM_MUNKI_UNINSTALLCHECK_SCRIPT, ITEM_MUNKI_UNINSTALL_SCRIPT
    global ITEM_MUNKI_INSTALLCHECK_SCRIPT, ITEM_MUNKI_PREINSTALL_SCRIPT
    ITEM_MUNKI_NAME = "Configuration_Managed_Software_Center_admin_only"
    ITEM_MUNKI_VERSION = raw_input("Version (example: 2016.10): ")
    ITEM_MUNKI_UNINSTALLCHECK_SCRIPT = "uninstallcheck.py"
    ITEM_MUNKI_UNINSTALL_SCRIPT = "uninstall.sh" # fake, work is done by the "uninstall check"
    ITEM_MUNKI_INSTALLCHECK_SCRIPT = "installcheck.py"
    ITEM_MUNKI_PREINSTALL_SCRIPT = "preinstall.py"

    # Generate nopkg item (pkginfo):
    write_pkginfo_and_add_to_repo()

if __name__ == "__main__":
    main()
