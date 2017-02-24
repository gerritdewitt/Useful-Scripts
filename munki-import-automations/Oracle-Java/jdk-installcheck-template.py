#!/usr/bin/env python

# jdk-installcheck-template.py
# Install check script for determining if a JDK
# update is applicable.  Uses java_home to read
# the most recent version installed and compares
# that to a given version of the JDK.
# To be used as an installcheck script for JDK
# updates delivered via Munki.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2015-09-29, 2016-10-31, 2016-11-01, 2016-12-12/13.
# 2017-02-24.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import os, xml, plistlib, subprocess, sys, logging
from distutils.version import LooseVersion, StrictVersion

global JDK_VERSION_DESIRED
JDK_VERSION_DESIRED = "__%jdk_version%__"

def macos_java_home_get_latest_jdk_installed():
    '''Calls /usr/libexec/java_home to get a list
        of Java VMs installed.  Returns the latest
        version or an empty string if no JVM is
        installed (as tested by java_home).'''
    jdk_version_installed_list = []
    max_jdk_vers_installed = ''
    try:
        output = subprocess.check_output(['/usr/libexec/java_home',
                               '-xml'])
    except subprocess.CalledProcessError:
        output = ''
    if output:
        try:
            # Note that XML from java_home returns a top-level <array>!
            output_list = plistlib.readPlistFromString(output)
        except xml.parsers.expat.ExpatError:
            output_list = []
    # Loop over JVM dictionaries:
    for jvm_dict in output_list:
        try:
            jdk_version_installed_list.append(jvm_dict['JVMVersion'])
        except KeyError:
            pass
    # Sort list of JVM versions:
    if jdk_version_installed_list:
        jdk_version_installed_list.sort()
        try:
            max_jdk_vers_installed = jdk_version_installed_list[-1]
        except IndexError:
            pass
    # Return:
    return max_jdk_vers_installed

def main():
    '''Main logic.'''
    # Get latest JDK installed:
    latest_jdk_installed = macos_java_home_get_latest_jdk_installed()
    # If JDK present:
    if latest_jdk_installed:
        if LooseVersion(latest_jdk_installed) < LooseVersion(JDK_VERSION_DESIRED):
            logging.error("Latest installed JDK version appears to be: %s" % latest_jdk_installed)
            logging.error("  Desired version is %s; requesting JDK update..." % JDK_VERSION_DESIRED)
            sys.exit(0) # installation requested
    # Default:
    sys.exit(1) # installation NOT requested

if __name__ == "__main__":
    main()
