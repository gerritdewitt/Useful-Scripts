#!/usr/bin/env python

# installcheck.py
# Script for checking to see if a named local
# user account should be removed.
# Documentation & References: See closest ReadMe.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# This file created 2015-08-25, 2015-11-10 (extensions), 2016-02-19, 2016-08-16, 2016-08-29.
# 2017-01-30.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.

import sys, plistlib, xml, subprocess, os, datetime, math, logging

global LOCAL_USER_NAME, LOCAL_USER_MAX_LIFETIME_DAYS
LOCAL_USER_NAME = 'local_account_name' # Replace with the name of your local user account to be purged.
LOCAL_USER_MAX_LIFETIME_DAYS = int(10) # Replace with the ideal lifetime in days after which the account is considered a removal candidate.

def macos_user_exists(given_user_name):
    '''Returns true iff the given user account exists
        in the local directory node, false otherwise.'''
    try:
        subprocess.check_call(['/usr/bin/dscl',
                               '/Local/Default',
                               'read',
                               '/Users/%s' % given_user_name,
                               'RecordName'])
        return True
    except subprocess.CalledProcessError:
        return False

def macos_get_creation_time_for_user(given_user_name):
    '''Returns the creation timestamp for the given user account
        in the local directory node.  Returns a time close
        to the epoch if the account creation timestamp cannot
        be determined.'''
    output = ''
    output_dict = {}
    account_policy_str = ''
    account_policy_dict = {}
    account_creation_float = 1.0 # impossible past
    account_creation_timestamp = datetime.datetime.fromtimestamp(account_creation_float) # impossible past
    # Run dscl:
    try:
        output = subprocess.check_output(['/usr/bin/dscl',
                                          '-plist',
                                          '/Local/Default',
                                          'read',
                                          '/Users/%s' % given_user_name,
                                          'dsAttrTypeNative:accountPolicyData'])
    except subprocess.CalledProcessError:
        pass
    if output:
        try:
            output_dict = plistlib.readPlistFromString(output)
        except xml.parsers.expat.ExpatError:
            pass
    # Parse:
    if output_dict:
        try:
            account_policy_value = output_dict['dsAttrTypeNative:accountPolicyData']
        except KeyError:
            account_policy_value = []
        try:
            account_policy_str = account_policy_value[0]
        except IndexError:
            pass
    if account_policy_str:
        try:
            account_policy_dict = plistlib.readPlistFromString(account_policy_str)
        except xml.parsers.expat.ExpatError:
            pass
    if account_policy_dict:
        try:
            account_creation_float = account_policy_dict['creationTime']
        except KeyError:
            pass
    # Convert account creation timestamp to next epoch integer:
    if account_creation_float > 1.0:
        try:
            account_creation_timestamp = datetime.datetime.fromtimestamp(account_creation_float)
        except ValueError:
            pass
    # Return:
    return account_creation_timestamp

def main():
    '''Main logic for this script'''
    # Check for account; if not present, return 1 (do nothing).
    if not macos_user_exists(LOCAL_USER_NAME):
        logging.info("The %s account does not exist in the local directory node." % LOCAL_USER_NAME)
        sys.exit(1) # skip because the account is not present

    # Here if the account exists:
    print "The %s account does exist in the local directory node.  Checking its creation timestamp..." % LOCAL_USER_NAME
    creation_time = macos_get_creation_time_for_user(LOCAL_USER_NAME)
    print "Creation timestamp for %(user)s is %(ts)s." % {"user":LOCAL_USER_NAME,"ts":str(creation_time)}
    time_delta = datetime.datetime.utcnow() - creation_time
    time_delta_days = math.fabs(time_delta.days)
    print "Days since creation for %(user)s is %(days)s." % {"user":LOCAL_USER_NAME,"days":str(time_delta_days)}
    if time_delta_days <= LOCAL_USER_MAX_LIFETIME_DAYS:
        print "Will not take any action on %(user)s because it is too young (threshold %(days)s)." % {"user":LOCAL_USER_NAME,"days":str(LOCAL_USER_MAX_LIFETIME_DAYS)}
        sys.exit(1) # skip because the account is too young to delete
    # Here if the account exists and it is past LOCAL_USER_MAX_LIFETIME_DAYS:
    print "Should remove %(user)s because it is older than %(days)s days." % {"user":LOCAL_USER_NAME,"days":str(LOCAL_USER_MAX_LIFETIME_DAYS)}
    sys.exit(0)

# Run main.
if __name__ == "__main__":
    main()
