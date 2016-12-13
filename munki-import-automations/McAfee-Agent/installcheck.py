#!/usr/bin/env python

# installcheck.py
# A simple script to determine if installing the
# McAfee Agent is necessary by version string comparison.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-09-29, 2016-10-31, 2016-11-01, 2016-12-12/13.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, sys, logging
import xml.etree.ElementTree as et
from distutils.version import LooseVersion, StrictVersion

global MCAFEE_AGENT_VERSION_DESIRED
MCAFEE_AGENT_VERSION_DESIRED = "__%app_version%__"

global MCAFEE_AGENT_CONFIG_FILE_PATHS
MCAFEE_AGENT_CONFIG_FILE_PATHS = []
# in order of preference:
MCAFEE_AGENT_CONFIG_FILE_PATHS.append("/etc/ma.d/EPOAGENT3000/config.xml")
MCAFEE_AGENT_CONFIG_FILE_PATHS.append("/etc/cma.d/EPOAGENT3700MACX/config.xml")

def read_agent_version(given_file_path):
    '''Read version information if possible.
        Returns 0 if not possible.'''
    file_content = ''
    file_content_xml_root = []
    agent_vers = "0"
    if os.path.exists(given_file_path):
        try:
            file_handle = open(given_file_path,'r')
            file_content = file_handle.read()
            file_handle.close()
        except IOError:
            pass
    if file_content:
        try:
            file_content_xml_tree = et.ElementTree(et.fromstring(file_content))
            file_content_xml_root = file_content_xml_tree.getroot()
        except xml.etree.ElementTree.ParseError:
            pass
    for el in file_content_xml_root:
        if el.tag.lower() == "version":
            agent_vers = el.text
            break
    return agent_vers

def main():
    '''Main logic.'''
    # If all config files are missing:
    results = []
    for file_path in MCAFEE_AGENT_CONFIG_FILE_PATHS:
        results.append(os.path.exists(file_path))
    # If results are all False...
    if True not in results:
        logging.error("All known McAfee Agent config files missing; requesting McAfee Agent install...")
        sys.exit(0) # ...installation requested
    # Config present; read version starting at top of MCAFEE_AGENT_CONFIG_FILE_PATHS:
    agent_version_measured = "0"
    for file_path in MCAFEE_AGENT_CONFIG_FILE_PATHS:
        agent_version_measured = read_agent_version(file_path)
        if agent_version_measured != "0":
            break
    # Version comparisons:
    if LooseVersion(agent_version_measured) < LooseVersion(MCAFEE_AGENT_VERSION_DESIRED):
        logging.error("McAfee Agent installed version appears to be: %s" % agent_version_measured)
        logging.error("  Desired version is %s; requesting McAfee Agent install..." % MCAFEE_AGENT_VERSION_DESIRED)
        sys.exit(0) # installation requested
    # Default:
    sys.exit(1) # installation NOT requested


if __name__ == "__main__":
    main()
