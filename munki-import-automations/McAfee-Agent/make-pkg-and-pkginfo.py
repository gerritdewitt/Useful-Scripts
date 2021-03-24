#!/usr/bin/env python

# make-pkg-and-pkginfo.py
# Script for generating a disk image with the McAfee Agent
# install.sh bash archive for deployment with Munki.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-08-24/28, 2015-09-11 (config profile and pkginfo creation), 2015-11-24 (conditions), 2015-11-25, 2016-10-04 (Mathematica), 2016-11-03, 2016-12-12/13.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, plistlib, subprocess, sys, shutil

global ITEMS_TO_COPY
ITEMS_TO_COPY = []
COPY_ITEM = {'destination_path':"/private/tmp",
'source_item':"install.sh",
'destination_item':"install.sh"}
ITEMS_TO_COPY.append(COPY_ITEM)

def generate_dmg(given_app_version,given_vendor_bash_archive):
    '''Generates the dmg with the item(s).  Returns path to udzo dmg.'''
    # Paths and cleanup:
    sparse_dmg_path = "/private/tmp/%(name)s-%(vers)s.sparseimage" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version}
    udzo_dmg_path = "/private/tmp/%(name)s-%(vers)s.dmg" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version}
    sparse_dmg_mount_path = "/private/tmp/%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version}
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
    # Copy vendor installer to dmg:
    dmg_item_path = os.path.join(sparse_dmg_mount_path,ITEMS_TO_COPY[0]['source_item'])
    shutil.copy(given_vendor_bash_archive,dmg_item_path)
    try:
        subprocess.check_call(['/usr/sbin/chown',
                               'root:admin',
                               dmg_item_path])
    except subprocess.CalledProcessError:
       print "Error setting owners on %s!" % dmg_item_path
       return None
    try:
        subprocess.check_call(['/bin/chmod',
                               '0755',
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

def generate_pkginfo(given_dmg_path,given_app_version):
    '''Makes the pkginfo for this item.'''
    munki_repo_pkginfo_path = os.path.join(MUNKI_PKGSINFO_PATH,"%(name)s-%(vers)s" % {"name": ITEM_MUNKI_NAME,"vers":given_app_version})
    print "Pkginfo will be %s." % munki_repo_pkginfo_path
    
    # Installcheck script content:
    h = open(ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH,'r')
    installcheck_script_content = h.read()
    h.close()
    installcheck_script_content = installcheck_script_content.replace("__%app_version%__",given_app_version)
    item_munki_installcheck_path = "/private/tmp/%s_installcheck_script.py" % ITEM_MUNKI_NAME
    h = open(item_munki_installcheck_path,'w')
    h.write(installcheck_script_content)
    h.close()

    # Call makepkginfo:
    try:
        output = subprocess.check_output(['/usr/local/munki/makepkginfo',
                                          '--name=%s' % ITEM_MUNKI_NAME,
                                          '--installcheck_script=%s' % item_munki_installcheck_path,
                                          '--postinstall_script=%s' % ITEM_MUNKI_POSTINSTALL_PATH,
                                          '--description=%s' % ITEM_MUNKI_DESCRIPTION,
                                          '--catalog=%s' % ITEM_MUNKI_CATALOG_NAME,
                                          '--unattended_install',
                                          '--pkgvers=%s' % given_app_version,
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
    # For the present, this isn't something we use Munki to remove:
    output_dict['uninstallable'] = False
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
    global ITEM_MUNKI_NAME,ITEM_MUNKI_DISP_NAME,ITEM_MUNKI_MIN_OS, ITEM_MUNKI_CATALOG_NAME, ITEM_MUNKI_DESCRIPTION, ITEM_MUNKI_DEVELOPER_NAME, ITEM_MUNKI_CATEGORY
    ITEM_MUNKI_NAME = "McAfee_Agent"
    ITEM_MUNKI_DISP_NAME = "McAfee Agent"
    ITEM_MUNKI_MIN_OS = "10.10.5"
    ITEM_MUNKI_CATALOG_NAME = "software"
    ITEM_MUNKI_DESCRIPTION = "Installs the McAfee Agent, which then gets various products from the EPO/ENS server."

    global THIS_DIR
    THIS_DIR = os.path.dirname(os.path.realpath(__file__))

    global ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH, ITEM_MUNKI_POSTINSTALL_PATH
    ITEM_MUNKI_INSTALLCHECK_TEMPLATE_PATH = os.path.join(THIS_DIR, "installcheck.py")
    ITEM_MUNKI_POSTINSTALL_PATH = os.path.join(THIS_DIR, "postinstall.py") # Postinstall script needs no adjustment.

    # Gather item info:
    app_version = raw_input("McAfee version: ")
    vendor_install_script_path = raw_input("Path to McAfee install.sh: ")

    # Generate disk image and copy it to the munki repo:
    generated_dmg_path = generate_dmg(app_version,vendor_install_script_path)
    if not generated_dmg_path:
        print "Failed to create dmg."
        sys.exit(1)
    repo_dmg_path = copy_to_repo(generated_dmg_path)
    if not repo_dmg_path:
        print "Failed to copy dmg to munki repo."
        sys.exit(1)
    # Generate pkginfo:
    if not generate_pkginfo(repo_dmg_path,app_version):
        print "Failed create pkginfo."
        sys.exit(1)
    # All OK if here:
    sys.exit(0)

if __name__ == "__main__":
    main()
