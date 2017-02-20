#!/bin/sh

#  make-installer-pkg.sh
#  GSU Scripts for properly packaging Alertus software.

# Written by Gerrit DeWitt (gdewitt@gsu.edu)
# 2016-04-11, 2016-05-11, 2016-06-03, 2016-06-06.
# Copyright Georgia State University.
# This script uses publicly-documented methods known to those skilled in the art.
# References: See top level Read Me.

declare -x PATH="/usr/bin:/bin:/usr/sbin:/sbin"

# MARK: VARIABLES

# General paths:
declare -x THIS_DIR=$(dirname "$0")

# Package attrs:
declare -x PACKAGE_SCRIPTS_DIR="$THIS_DIR/package-scripts"

# Things we gather:
declare -x SRC_ALERTUS_INSTALLER_DMG
declare -x ALERTUS_DESKTOP_CONFIG_FILE_PATH
declare -x LOGO_FILE_PATH
declare -x PACKAGE_VERSION
declare -x PACKAGE_PATH

# Temp dirs:
declare -x TEMP_DIR="$THIS_DIR/tmp"
declare -x TEMP_DIR_MOUNT_POINT="$TEMP_DIR/mount-point"

# Sources:
declare -x ALERTUS_DESKTOP_APP_NAME="Alertus Desktop.app"
declare -x ALERTUS_DESKTOP_LAUNCH_AGENT_NAME="com.alertus.AlertusDesktopClient.plist"

# Paths in pkg root:
declare -x PACKAGE_ROOT_DIR="$THIS_DIR/package-root"
declare -x PR_APPS_DIR="$PACKAGE_ROOT_DIR/Applications"
declare -x PR_LA_DIR="$PACKAGE_ROOT_DIR/Library/LaunchAgents"
declare -x PR_APP_SUP_DIR="$PACKAGE_ROOT_DIR/Library/Application Support/Alertus Technologies/Desktop Alert"

# MARK: gather_materials()
# Sources installer materials.
function gather_materials(){
echo "This script builds a proper installer package for Alertus Desktop, including properly wrapping the configuration within the installer package.  The resulting package is suitable for mass deployment via Munki, Casper, Absolute Manage, etc."
echo "\nSource Materials"
echo "Provide the full path to the Alertus Desktop DMG containing an unmodified PKG:"
read SRC_ALERTUS_INSTALLER_DMG

echo "Provide the full path to the AlertusDesktopAlert.exe.config file:"
read ALERTUS_DESKTOP_CONFIG_FILE_PATH

echo "Provide the full path to the logo1.gif file:"
read LOGO_FILE_PATH

echo "Enter a version number (for example YYYY.MM like 2016.07):"
read PACKAGE_VERSION

echo "Enter an identifier for the Apple pkg (example: edu.someuniversity.alertus.desktop):"
read PACKAGE_IDENTIFIER

PACKAGE_PATH="$THIS_DIR/Alertus_Desktop-$PACKAGE_VERSION.pkg"

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
mkdir -p "$PR_APPS_DIR" && echo "Created Applications directory in package root."
mkdir -p "$PR_LA_DIR" && echo "Created LaunchAgents directory in package root."
mkdir -p "$PR_APP_SUP_DIR" && echo "Created App Support directory in package root."
# Copy app into package root:
cp -R "$TEMP_DIR/$ALERTUS_DESKTOP_APP_NAME" "$PR_APPS_DIR/$ALERTUS_DESKTOP_APP_NAME" && echo "Copied app to Applications directory in package root."
# Copy launch agent into package root:
cp "$THIS_DIR/$ALERTUS_DESKTOP_LAUNCH_AGENT_NAME" "$PR_LA_DIR/$ALERTUS_DESKTOP_LAUNCH_AGENT_NAME" && echo "Copied launch agent to LaunchAgents directory in package root."
# Copy config file into package root:
cp "$ALERTUS_DESKTOP_CONFIG_FILE_PATH" "$PR_APP_SUP_DIR/AlertusDesktopAlert.exe.config" && echo "Copied config file to App Support directory in package root."
# Copy logo file into package root:
cp "$LOGO_FILE_PATH" "$PR_APP_SUP_DIR/logo1.gif" && echo "Copied logo file to App Support directory in package root."
# Set permisions on package root:
chmod -R 0755 "$PACKAGE_ROOT_DIR" && echo "Set permissions on package root."
chmod 0644 "$PACKAGE_ROOT_DIR/Library/LaunchAgents/$ALERTUS_DESKTOP_LAUNCH_AGENT_NAME" && echo "Set permissions on launch agent in package root."
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
    echo "To deploy this package with Munki, follow the directions on the wiki."
fi
}

# MARK: extract_alertus_pkg_components()
# Calls pkgutil to expand the Alertus pkg and extract pkgroot materials:
function extract_alertus_pkg_components(){
# Mount the Alertus dmg:
    mkdir -p "$TEMP_DIR_MOUNT_POINT"
    hdiutil attach "$SRC_ALERTUS_INSTALLER_DMG" -mountpoint "$TEMP_DIR_MOUNT_POINT"
# Copy pkg and eject dmg:
    cp "$TEMP_DIR_MOUNT_POINT"/*.pkg "$TEMP_DIR/installer.pkg"
    hdiutil eject "$TEMP_DIR_MOUNT_POINT"
# Call pkgutil:
    pkgutil --expand "$TEMP_DIR/installer.pkg" "$TEMP_DIR/installer"
    if [ ! -d "$TEMP_DIR/installer" ]; then
        echo "Error: Failed to expand the Alertus package with pkgutil."
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
extract_alertus_pkg_components
build_custom_pkg
prepost_cleanup
