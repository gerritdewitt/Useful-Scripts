#!/usr/bin/env python

# create-munki-group.py
# Script for programmatically generating a Munki
# computer group.
# Documentation & References: See closest ReadMe.md

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2017-05-26
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, plistlib, sys

# Templates for groups:
# Base:
CATALOGS_BASE = ["configuration","software"]

INCLUDES_MANIFESTS_BASE = []
INCLUDES_MANIFESTS_BASE.append("includes/software-common-managed_updates")
INCLUDES_MANIFESTS_BASE.append("includes/software-common-optional_installs")
INCLUDES_MANIFESTS_BASE.append("includes/software-common-managed_installs")
INCLUDES_MANIFESTS_BASE.append("includes/configuration-common")
INCLUDES_MANIFESTS_BASE.append("includes/conditions")
global INCLUDES_MANIFESTS_LABS, INCLUDES_MANIFESTS_INDIVIDUALS
INCLUDES_MANIFESTS_LABS = ["includes/configuration-common-labs"]
INCLUDES_MANIFESTS_INDIVIDUALS = []

global MANAGED_INSTALLS_LABS, MANAGED_INSTALLS_INDIVIDUALS
MANAGED_INSTALLS_LABS = []
MANAGED_INSTALLS_INDIVIDUALS = ["Configuration_Base_Loginwindow_and_Sessions.mobileconfig"]

global MANIFEST_EXTENSION_DICT_LABS, MANIFEST_EXTENSION_DICT_INDIVIDUALS
MANIFEST_EXTENSION_DICT_LABS = {}
MANIFEST_EXTENSION_DICT_INDIVIDUALS = {"conditional_items":[
{"condition":"machine_type == \"desktop\"",
"optional_installs":["Alertus_Panic_Button"]
}
]}

global TEMPLATE_GROUP_BASE
TEMPLATE_GROUP_BASE = {"_metadata":{},
                       "catalogs":CATALOGS_BASE,
                       "included_manifests":INCLUDES_MANIFESTS_BASE}


def create_group():
    '''Method to make a group from a template.'''
    
    # Prompt: type of group:
    print '''
Creating a new group.  Please select a template:
  - individual: for groups to be used for individually-assigned computers, including faculty and staff
  - lab: for labs and classrooms
'''
    group_template_type = raw_input("Group Type: ").strip().lower()
    if group_template_type not in ["individual","lab"]:
        print "Invalid group type; please try again."
        return False
    # Prompt: Group Filesystem Name:
    print '''
Please choose a filesystem name for this group.  Names should be lower-case and exclude spaces.
'''
    group_filesystem_name = raw_input("Group Filesystem Name: ").strip().lower()
    if not group_filesystem_name:
        print "Group Filesystem Name cannot be blank; please try again."
        return False
    group_file_path = os.path.join(MUNKI_GROUP_MANIFESTS_PATH,group_filesystem_name)
    if os.path.exists(group_file_path):
        print "File named %s already exists in Munki group manifests directory; please try again." % group_filesystem_name
        return False
    # Prompt: Group Display Name:
    print '''
Provide a display name for this group.  This is the user-visible name that appears in the Munki Enrollment Client.
'''
    group_display_name = raw_input("Group Display Name: ")
    if not group_display_name:
        print "Group Display Name cannot be blank; please try again."
        return False
    # Prompt: Group Description:
    print '''
Provide a description for this group.  This appears in the Munki Enrollment Client.
'''
    group_description = raw_input("Group Description: ")
    # Prompt: Default Computer Name Prefix:
    print '''
Provide a default naming prefix that the Munki Enrollment Client can suggest for names.
Must be 8 characters or less.
'''
    group_computer_name_prefix = raw_input("Computer Name Prefix: ")
    if len(group_computer_name_prefix) > 8:
        print "Computer Name Prefix must be 8 characters or less; please try again."
        return False

    # Create group dict starting with base:
    group_manifest_dict = TEMPLATE_GROUP_BASE
    # Add _metadata:display_name (manditory):
    group_manifest_dict["_metadata"]["display_name"] = group_display_name
    # Add _metadata:description (optional):
    if group_description:
        group_manifest_dict["_metadata"]["description"] = group_description
    # Add _metadata:computer_name_prefix (optional):
    if group_computer_name_prefix:
        group_manifest_dict["_metadata"]["computer_name_prefix"] = group_computer_name_prefix

    # Lab group:
    if group_template_type == "lab":
        # Additional includes manifests:
        if INCLUDES_MANIFESTS_LABS:
            group_manifest_dict["included_manifests"].extend(INCLUDES_MANIFESTS_LABS)
        # Managed installs:
        if MANAGED_INSTALLS_LABS:
            group_manifest_dict["managed_installs"] = MANAGED_INSTALLS_LABS
        # Other dict items to merge:
        if MANIFEST_EXTENSION_DICT_LABS:
            group_manifest_dict.update(MANIFEST_EXTENSION_DICT_LABS)
    # Individual group:
    elif group_template_type == "individual":
        # Additional includes manifests:
        if INCLUDES_MANIFESTS_INDIVIDUALS:
            group_manifest_dict["included_manifests"].extend(INCLUDES_MANIFESTS_INDIVIDUALS)
        # Managed installs:
        if MANAGED_INSTALLS_INDIVIDUALS:
            group_manifest_dict["managed_installs"] = MANAGED_INSTALLS_INDIVIDUALS
        # Other dict items to merge:
        if MANIFEST_EXTENSION_DICT_INDIVIDUALS:
            group_manifest_dict.update(MANIFEST_EXTENSION_DICT_INDIVIDUALS)

    # Write group manifest:
    try:
        plistlib.writePlist(group_manifest_dict,group_file_path)
        return True
    except IOError:
        print "ERROR: Could not save new group to %s!" % group_file_path
        return False

def main():
    '''Main logic.'''
    # Gather Munki repository info:
    global MUNKI_REPO_PATH, MUNKI_MANIFESTS_PATH, MUNKI_GROUP_MANIFESTS_PATH
    try:
        MUNKI_REPO_PATH = os.environ['MUNKI_REPO_PATH']
    except KeyError:
        MUNKI_REPO_PATH = raw_input("Munki repo base path: ")
    if not os.path.exists(MUNKI_REPO_PATH):
        print "Munki repository does not exist at %s!" % MUNKI_REPO_PATH
        sys.exit(1)
    MUNKI_MANIFESTS_PATH = os.path.join(MUNKI_REPO_PATH,'manifests')
    if not os.path.exists(MUNKI_MANIFESTS_PATH):
        print "Missing manifests dir at %s!" % MUNKI_MANIFESTS_PATH
        sys.exit(1)
    MUNKI_GROUP_MANIFESTS_PATH = os.path.join(MUNKI_MANIFESTS_PATH,'groups')
    if not os.path.exists(MUNKI_GROUP_MANIFESTS_PATH):
        print "Missing groups manifests dir at %s!" % MUNKI_GROUP_MANIFESTS_PATH
        sys.exit(1)

    # Ask what to do:
    print '''
Please choose an action:
  - To create a group, type "new-group" and press return.
'''
    manifest_action = raw_input("Action: ").strip().lower()
    if manifest_action not in ["new-group"]:
        print "Invalid action; please try again."
        sys.exit(1)

    # Create group:
    if manifest_action == "new-group":
        if not create_group():
            sys.exit(1)

if __name__ == "__main__":
    main()
