#!/bin/sh

#  make-installer-pkg.sh
#  GSU Scripts for properly packaging WebEx software

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2016-04-11, 2016-05-11, 2016-06-03, 2016-06-06, 2016-07-11.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.
# References: See top level Read Me.

declare -x PATH="/usr/bin:/bin:/usr/sbin:/sbin"

# MARK: VARIABLES

# General paths:
declare -x THIS_DIR=$(dirname "$0")

# Package attrs:
declare -x PACKAGE_IDENTIFIER="edu.gsu.webex.meeting-center"
declare -x PACKAGE_SCRIPTS_DIR="$THIS_DIR/package-scripts"

# Things we gather:
declare -x SRC_WEBEX_INSTALLER_DMG
declare -x PACKAGE_VERSION
declare -x PACKAGE_PATH

# Temp dirs:
declare -x TEMP_DIR="$THIS_DIR/tmp"
declare -x TEMP_DIR_MOUNT_POINT="$TEMP_DIR/mount-point"

# Sources:
declare -x WEBEX_PLUGIN_NAME="WebEx64.plugin"
declare -a WEBEX_APPS=("Meeting Center" "asannotation2" "convertpdf" "atmsupload") # determined by inspection of the Cisco WebEx MC postflight script

# Paths in pkg root:
declare -x PACKAGE_ROOT_DIR="$THIS_DIR/package-root"
declare -x PR_INET_PLUGINS_DIR="$PACKAGE_ROOT_DIR/Library/Internet Plug-Ins"
declare -x PR_APP_SUP_DIR="$PACKAGE_ROOT_DIR/Library/Application Support/WebEx Folder"

# MARK: gather_materials()
# Sources installer materials.
function gather_materials(){
    echo "This script builds a proper installer package for WebEx Meeting Center, making the plugin available to all users.  The resulting package is suitable for mass deployment via Munki, Casper, Absolute Manage, etc."
    echo "\nSource Materials"
    echo "Provide the full path to the WebEx Meeting Center DMG containing an unmodified PKG:"
    read SRC_WEBEX_INSTALLER_DMG

    echo "Enter a version number (for example YYYY.MM like 2016.07):"
    read PACKAGE_VERSION

    PACKAGE_PATH="$THIS_DIR/WebEx_Meeting_Center-$PACKAGE_VERSION.pkg"
}

# MARK: prepost_cleanup()
# Removes various temporary or intermediate directories and files used by the packaging process.
function prepost_cleanup(){
    if [ -d "$PACKAGE_ROOT_DIR" ]; then
        rm -rf "$PACKAGE_ROOT_DIR" && echo "Removed $PACKAGE_ROOT_DIR."
    fi
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR" && echo "Removed $TEMP_DIR."
    fi
}

# MARK: build_custom_pkg()
# Builds the component pkg.
function build_custom_pkg(){
    # Set permisions on package scripts dir:
    chmod -R 0755 "$PACKAGE_SCRIPTS_DIR" && echo "Set permissions on package scripts directory."
    # Create package root:
    mkdir -p "$PR_INET_PLUGINS_DIR" && echo "Created Internet Plugins directory in package root."
    mkdir -p "$PR_APP_SUP_DIR" && echo "Created App Support directory in package root."
    # Move plugin into package root:
    mv "$TEMP_DIR/$WEBEX_PLUGIN_NAME" "$PR_INET_PLUGINS_DIR/$WEBEX_PLUGIN_NAME" && echo "Moved Internet Plugin to pkg root."
    # Move everything else to app support:
    mv "$TEMP_DIR"/* "$PR_APP_SUP_DIR/" && echo "Moved everything else to App Support directory in package root."
    # For strange reasons, Cisco omitted ".app" on these items:
    for app_name in "${WEBEX_APPS[@]}"; do
        mv "$PR_APP_SUP_DIR/$app_name" "$PR_APP_SUP_DIR/$app_name.app" && echo "Added app extension to $app_name in App Support directory in package root."
    done
    # Set permisions on package root:
    chmod -R 0755 "$PACKAGE_ROOT_DIR" && echo "Set permissions on package root."
    echo "Using pkgbuild defaults.  Ownership will be root:wheel."
    # Remove ._ files from package root:
    find "$PACKAGE_ROOT_DIR" -name ._\* -exec rm {} \;
    # Remove .DS_Store files from package root:
    find "$PACKAGE_ROOT_DIR" -name .DS_Store -exec rm {} \;
    # Remove quarantine xattrs:
    xattr -d com.apple.quarantine "$PACKAGE_ROOT_DIR"
    # Build package:
    pkgbuild --root "$PACKAGE_ROOT_DIR" --identifier "$PACKAGE_IDENTIFIER" --scripts "$PACKAGE_SCRIPTS_DIR" --version "$PACKAGE_VERSION" "$PACKAGE_PATH" && echo "Built package."
    if [ ! -f "$PACKAGE_PATH" ]; then
        echo "Error: Failed to build package."
        exit 1
    else
        echo "Built package successfully.  It is located here:\n $PACKAGE_PATH"
    fi
}

# MARK: extract_webex_pkg_components()
# Calls pkgutil to expand the WebEx pkg and extract pkgroot materials:
function extract_webex_pkg_components(){
# Mount the WebEx dmg:
    mkdir -p "$TEMP_DIR_MOUNT_POINT"
    hdiutil attach "$SRC_WEBEX_INSTALLER_DMG" -mountpoint "$TEMP_DIR_MOUNT_POINT"
# Copy pkg and eject dmg:
    cp "$TEMP_DIR_MOUNT_POINT"/*.pkg "$TEMP_DIR/installer.pkg"
    hdiutil eject "$TEMP_DIR_MOUNT_POINT"
# Call pkgutil:
    pkgutil --expand "$TEMP_DIR/installer.pkg" "$TEMP_DIR/installer"
    if [ ! -d "$TEMP_DIR/installer" ]; then
        echo "Error: Failed to expand the WebEx package with pkgutil."
        exit 1
    fi
# Find and move payload:
    PAYLOAD_PATH="$(find "$TEMP_DIR/installer" -name Payload)" && echo "Payload found at $PAYLOAD_PATH."
    mv "$PAYLOAD_PATH" "$TEMP_DIR/Payload.pax.gz" && echo "Moved Payload to $TEMP_DIR."
# Expand payload:
    cd "$TEMP_DIR"
    gunzip "Payload.pax.gz"
    pax -r -p e -f "Payload.pax"
    rm "Payload.pax"
    cd ..
}

# MARK: main()
prepost_cleanup
gather_materials
extract_webex_pkg_components
build_custom_pkg
prepost_cleanup