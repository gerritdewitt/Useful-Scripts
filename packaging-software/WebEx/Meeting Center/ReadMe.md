About
----------
This folder contains materials for creating an Apple Installer package with WebEx Meeting Center software.

The _make-installer-pkg.sh_ script is an “admin script” designed to be run from an admin Mac.  It will ask you for version information and installation source materials provided by the vendor.

Why Repackage
----------
We repackage the WebEx Meeting Center because:
   * The vendor's installer, while an Installer package itself, only installs to the user's home directory.  This is obviously not tenable for mass deployment.
   * The vendor's installer package does not provide correct version information in its package metadata.  Therefore, mass deployment systems that correctly depend on pkg receipts will not be able to determine the actual installed version.

Creating Package
----------
To build the installer package, simply run the _make-installer-pkg.sh_ script.  The script is interactive; it will produce an Apple Installer package.

The script asks for the following information:
   * The path to the disk image containing the unmodified WebEx Meeting Center installer pkg.
   * A version number (You can use year.month or the version number provided by the vendor.  The latter is preferable.)

The resulting package is named _WebEx_Meeting_Center-&lt;version&gt;.pkg_.  It is in the same directory as the _make-installer-pkg.sh_ script.

Deploying with Munki
----------
To deploy, add the resulting installer package to the Munki repository and configure it as an optional or managed install:

For example:
<pre>
# Copy to repo:
sudo cp WebEx_Meeting_Center-30.9.0.10050.pkg /mounts/munki-repo/pkgs/
# Generate pkginfo:
sudo -s
makepkginfo --unattended_install --name WebEx_Meeting_Center --displayname="WebEx Meeting Center" \
--pkgvers=30.9.0.10050 --catalog=software --developer="Cisco" --category="WebEx" \
/mounts/munki-repo/pkgs/WebEx_Meeting_Center-30.9.0.10050.pkg > /mounts/munki-repo/pkgsinfo/WebEx_Meeting_Center-30.9.0.10050
exit
# Update catalogs:
sudo makecatalogs
# Add to manifest:
sudo manifestutil add-pkg WebEx_Meeting_Center --section optional_installs --manifest some_manifest
</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/pkgutil.1.html
2. https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/pkgbuild.1.html
