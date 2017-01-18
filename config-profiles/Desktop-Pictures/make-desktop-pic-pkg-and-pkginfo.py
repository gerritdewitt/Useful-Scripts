#!/usr/bin/env python

# make-desktop-pic-pkg-and-pkginfo.py
# Script deploying a custom Desktop Picture via Munki:
#   (a) creating a dmg (pkg) with the picture file itself
#   (b) adding that dmg to the Munki repo and generating its pkginfo
#       - on client computers, the profile will be installed to /Library/Desktop Pictures/Managed Desktop Picture.png
#   (d) referencing a configuration profile to set the picture as a requirement
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24/28, 2015-09-11 (config profile and pkginfo creation), 2015-11-24 (conditions)
# 2015-11-25 (Mathematica), 2016-01-08 (Ink2Go), 2016-04-26.
# 2017-01-17/18.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, uuid, plistlib, subprocess, sys, shutil

global ITEMS_TO_COPY
ITEMS_TO_COPY = []
COPY_ITEM = {'destination_path':"/Library/Desktop Pictures",
'source_item':"Managed Desktop Picture.png",
'destination_item':"Managed Desktop Picture.png"}
ITEMS_TO_COPY.append(COPY_ITEM)

def generate_dmg(given_picture_file_source_path):
    '''Generates the dmg with the item(s).  Returns path to udzo dmg.'''
    # Paths and cleanup:
    sparse_dmg_path = "/private/tmp/%(name)s-%(vers)s.sparseimage" % {"name": ITEM_MUNKI_NAME,"vers":ITEM_MUNKI_VERSION}
    udzo_dmg_path = "/private/tmp/%(name)s-%(vers)s.dmg" % {"name": ITEM_MUNKI_NAME,"vers":ITEM_MUNKI_VERSION}
    sparse_dmg_mount_path = "/private/tmp/%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":ITEM_MUNKI_VERSION}
    if os.path.exists(sparse_dmg_path):
        os.unlink(sparse_dmg_path)
    if os.path.exists(udzo_dmg_path):
        os.unlink(udzo_dmg_path)
    if os.path.exists(sparse_dmg_mount_path):
        shutil.rmtree(sparse_dmg_mount_path)
    # Create sparse dmg:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'create',
                               '-nospotlight',
                               '-srcowners',
                               'on',
                               '-type',
                               'SPARSE',
                               '-volname',
                               ITEM_MUNKI_NAME,
                               '-fs',
                               'Journaled HFS+',
                               '-size',
                               '50m',
                               '-layout',
                               'NONE',
                               sparse_dmg_path])
    except subprocess.CalledProcessError:
        print "Error creating sparse dmg!"
        return None
    # Mount sparse dmg:
    try:
        os.mkdir(sparse_dmg_mount_path)
    except OSError:
        print "Error creating mount path at %s!" % sparse_dmg_mount_path
        return None
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'attach',
                               '-mountpoint',
                               sparse_dmg_mount_path,
                               sparse_dmg_path])
    except subprocess.CalledProcessError:
        print "Error mounting sparse dmg at %s!" % sparse_dmg_mount_path
        return None
    # Copy items:
    dmg_item_path = os.path.join(sparse_dmg_mount_path,"Managed Desktop Picture.png")
    shutil.copy(given_picture_file_source_path,dmg_item_path)
    try:
        subprocess.check_call(['/usr/sbin/chown',
                               'root:admin',
                               dmg_item_path])
    except subprocess.CalledProcessError:
       print "Error setting owners on %s!" % dmg_item_path
       return None
    try:
        subprocess.check_call(['/bin/chmod',
                               '0644',
                               dmg_item_path])
    except subprocess.CalledProcessError:
       print "Error setting perms on %s!" % dmg_item_path
       return None
    # Eject sparse dmg:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'eject',
                               sparse_dmg_mount_path])
    except subprocess.CalledProcessError:
        print "Error ejecting sparse dmg at %s!" % sparse_dmg_mount_path
        return None
    # Convert dmg to compressed:
    try:
        subprocess.check_call(['/usr/bin/hdiutil',
                               'convert',
                               '-format',
                               'UDZO',
                               '-o',
                               udzo_dmg_path,
                               sparse_dmg_path])
    except subprocess.CalledProcessError:
        print "Error creating compressed dmg!"
        return None
    # Remove sparse dmg:
    os.unlink(sparse_dmg_path)

    return udzo_dmg_path

def copy_to_repo(given_dmg_path):
    '''Copies the dmg to the munki repo. Returns path to item in repo.'''
    # Paths and cleanup:
    munki_repo_pkg_path = os.path.join(MUNKI_PKGS_PATH,os.path.basename(given_dmg_path))
    print "Pkg in munki repo will be %s." % munki_repo_pkg_path
    # Check for existing pkg:
    if os.path.exists(munki_repo_pkg_path):
        print "Item already in munki repo: %s" % munki_repo_pkg_path
        return None
    # Copy to repo and set perms:
    shutil.copy(given_dmg_path,munki_repo_pkg_path)
    try:
        subprocess.check_call(['/bin/chmod',
                               '755',
                               munki_repo_pkg_path])
    except subprocess.CalledProcessError:
       print "Error setting perms on %s!" % munki_repo_pkg_path
       return None
    # Remove src dmg:
    os.unlink(given_dmg_path)
    return munki_repo_pkg_path

def generate_pkginfo(given_dmg_path):
    '''Makes the pkginfo for this item.'''
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":ITEM_MUNKI_VERSION})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % ITEM_MUNKI_NAME,
                                          '--unattended_install',
                                          '--catalog=configuration',
                                          '--pkgvers=%s' % ITEM_MUNKI_VERSION,
                                          '--displayname=%s' % ITEM_MUNKI_DISP_NAME,
                                          '--itemname=%s' % ITEMS_TO_COPY[0]['source_item'],
                                          '--destinationpath=%s' % ITEMS_TO_COPY[0]['destination_path'],
                                          given_dmg_path])
    except subprocess.CalledProcessError:
        print "Error creating pkginfo!"
        return False
    if output:
        output_dict = plistlib.readPlistFromString(output)
    # Other keys if defined:
    try:
        output_dict['minimum_os_version'] = ITEM_MUNKI_MIN_OS
    except NameError:
        pass
    try:
        output_dict['requires'] = ITEM_MUNKI_REQUIRES
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
    global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_VERSION, ITEM_MUNKI_REQUIRES
    ITEM_MUNKI_MIN_OS = "10.10.5"
    ITEM_MUNKI_CATALOG_NAME = "configuration"

    # Request the Desktop Picture file path:
    print '''
Please specify the path to a PNG image to use as a managed desktop picture.
'''
    picture_file_source_path = raw_input("Path to source PNG image file: ")
    # Request names:
    picture_name = raw_input("Name for this managed desktop picture (no spaces): ").replace(' ','')
    ITEM_MUNKI_NAME = "Desktop_Picture_%s" % picture_name
    picture_display_name = raw_input("Display name for this managed desktop picture: ")
    ITEM_MUNKI_DISP_NAME = "Desktop Picture (%s)" % picture_display_name
    # Request version:
    ITEM_MUNKI_VERSION = raw_input("Version for this managed desktop picture (example: 2016.10): ")
    # Request name of the configuration profile that will set this desktop picture:
    ITEM_MUNKI_REQUIRES = raw_input("Munki name of the configuration profile used to set managed desktop pictures: ")

    # Generate disk image and copy it to the munki repo:
    generated_dmg_path = generate_dmg(picture_file_source_path)
    if not generated_dmg_path:
        print "Failed to create dmg."
        sys.exit(1)
    repo_dmg_path = copy_to_repo(generated_dmg_path)
    if not repo_dmg_path:
        print "Failed to copy dmg to munki repo."
        sys.exit(1)

    # Generate pkginfo:
    if not generate_pkginfo(repo_dmg_path):
        print "Failed create pkginfo."
        sys.exit(1)
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
