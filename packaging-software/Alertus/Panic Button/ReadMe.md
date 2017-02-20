About
----------
This folder contains materials for creating an Apple Installer package with the Alertus Panic Button (aka Desktop Activator) software.

The _make-installer-pkg.sh_ script is an “admin script” designed to be run from an admin Mac.  It will ask you for version information and installation source materials provided by the vendor.  It is interactive and easily auditable.

Why Repackage
----------
We repackage the Alertus Panic Button software because:
   * The vendor's installer sources installation materials, namely configuration files and branding, from outside of the Installer pkg itself.  This has two immediate problems:
      * The installer pkg must be “wrapped” in a disk image or zip archive with the other materials.  The other materials must be in the same parent path as the pkg.
      * A custom Installer Plugin is used to accomplish the sourcing of out-of-pkg materials.  This only works in an Aqua session; mass deployment isn't possible with the vendor's method.
   * The vendor's installer sets filesystem permissions insecurely; this is similar to http://www.kb.cert.org/vuls/id/302544.

Creating Package
----------
To build the installer package, simply run the _make-installer-pkg.sh_ script.  The script is interactive; it will produce an Apple Installer package.

The script asks for the following information:
   * The path to the disk image containing the unmodified Alertus Panic Button installer pkg.
   * The path to the _DesktopActivator.org.properties_ file.
   * A version number (typically year.month as the package is specific to the customer).
   * A package identifier (e.g. edu.gsu.alertus.panicbutton)

The resulting package is named _Alertus_Panic_Button-&lt;version&gt;.pkg_.  It is in the same directory as the _make-installer-pkg.sh_ script.

Deploying with Munki
----------
To deploy, add the resulting installer package to the Munki repository and configure it as an optional or managed install.

For example:
<pre>
# Copy to repo:
sudo cp Alertus_Panic_Button-2016.06.pkg /mounts/munki-repo/pkgs/
# Generate pkginfo:
sudo -s
makepkginfo --unattended_install --name Alertus_Panic_Button --displayname="Alertus Panic Button" \
--pkgvers=2016.06 --catalog=software --developer="Alertus" --category="Alertus" \
/mounts/munki-repo/pkgs/Alertus_Panic_Button-2016.06.pkg > /mounts/munki-repo/pkgsinfo/Alertus_Panic_Button-2016.06
exit
# Update catalogs:
sudo makecatalogs
# Add to manifest:
sudo manifestutil add-pkg Alertus_Panic_Button --section optional_installs --manifest some_manifest
</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/pkgutil.1.html
2. https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/pkgbuild.1.html
3. https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/who.1.html
4. http://www.tutorialspoint.com/awk/awk_basic_examples.htm
5. launchctl “as user”:
   * https://derflounder.wordpress.com/2016/03/25/running-processes-in-os-x-as-the-logged-in-user-from-outside-the-users-account/
   * https://lists.macosforge.org/pipermail/launchd-dev/2015-July/001139.html
6. Inspection of the original Alertus software installer pkg and resulting launchd agent (_com.alertus.DesktopActivator.plist_)
