#!/usr/bin/env python

# postinstall.py
# Postinstall script for munki pkginfo for the McAfee Agent.
# Munki only copies the install.sh bash archive to the client.
# This script runs the bash archive, perfoming the installation.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-09-29, 2016-11-01/3, 2016-12-12/13.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.


import os, sys, logging, subprocess, shutil

global MCAFEE_AGENT_REMOVAL_SCRIPT_PATHS
MCAFEE_AGENT_REMOVAL_SCRIPT_PATHS = []
# in order of preference:
MCAFEE_AGENT_REMOVAL_SCRIPT_PATHS.append("/Library/McAfee/agent/scripts/uninstall.sh")
MCAFEE_AGENT_REMOVAL_SCRIPT_PATHS.append("/Library/McAfee/cma/uninstall.sh")

global MCAFEE_AGENT_LIBRARY_DIR_PATH
MCAFEE_AGENT_LIBRARY_DIR_PATH = "/Library/McAfee"

global MCAFEE_AGENT_INSTALLER_ARCHIVE_PATH
MCAFEE_AGENT_INSTALLER_ARCHIVE_PATH="/private/tmp/install.sh" # as installed by Munki

def run_script(given_args):
    '''Runs given script.  Returns True or False.'''
    try:
        subprocess.check_call(given_args)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    '''Main logic.'''
    # Run uninstallers:
    results = []
    for script_path in MCAFEE_AGENT_REMOVAL_SCRIPT_PATHS:
        if not os.path.exists(script_path):
            results.append(False)
        else:
            results.append( run_script([script_path]) )
    # If results are all False, note but continue.
    if True not in results:
        logging.error("Could not successfully run any of the known McAfee Agent removal scripts.")
    # Testing indicates this path must be absent
    # or the bash archive will fail:
    if os.path.exists(MCAFEE_AGENT_LIBRARY_DIR_PATH):
        try:
            shutil.rmtree(MCAFEE_AGENT_LIBRARY_DIR_PATH)
        except OSError:
            logging.error("Could not delete: %s" % MCAFEE_AGENT_LIBRARY_DIR_PATH)
            sys.exit(1)
    # Attempt installation of the bash archive:
    if not run_script([MCAFEE_AGENT_INSTALLER_ARCHIVE_PATH, "-i"]):
        logging.error("Could not install the new agent.")
        sys.exit(1)
    # Clean up:
    if os.path.exists(MCAFEE_AGENT_INSTALLER_ARCHIVE_PATH):
        try:
            os.unlink(MCAFEE_AGENT_INSTALLER_ARCHIVE_PATH)
        except OSError:
            pass
    # Success if this far:
    sys.exit(0)


if __name__ == "__main__":
    main()
