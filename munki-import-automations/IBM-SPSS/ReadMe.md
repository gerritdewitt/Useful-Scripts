IBM SPSS Statistics Materials
----------
Scripts and notes for deploying IBM SPSS Statistics with Munki.

## Challenges to Deployment ##
IBM provides a “silent installer” for SPSS Statistics as a bash archive in a disk image.  For this case, it's best for Munki to install the installer (the bash archive), then run the bash archive via postinstall script.

Historically, IBM has also provided a UI-driven VISE installer, but that is simply not suitable for mass deployment and automatic licensing.  Make sure you use the “silent installer” instead.

1. **Licensing**: The bash archive expects to be fed a path to an **installer properties file** which contains license information, including type, address of the license server, etc.  Fortunately, this format is rather straightforward.  IBM includes an example *installer.properties* file in the disk image with the bash archive.  The file is heavily commented, and there are examples and notes online.<sup>2</sup>
   - We could simply copy the *installer.properties* file from the disk image and modify it via postinstall script before calling the bash archive; however, our *make-pkginfo.py* script simply generates a very simple *installer.properties* file “from scratch” using information it collects when run.

2. **Install the Installer Problem**: Creating the *pkginfo* for this item requires knowing about Munki's “copy from dmg” installation method, and a solid understanding of how Munki determines if something is installed.  Uninstallation must also be considered, since *remove_copied_items* makes no sense for an “install the installer” case.<sup>1</sup>

3. **Java JVM Requirement**: The bash archive will fail to install unless an Oracle Java JVM is present.

## Deployment Overview ##
1. The IBM SPSS disk image should be copied to the Munki repository.  No changes are necessary to the disk image.
2. We'll programmatically create a *pkginfo* file for the “pkg” (the disk image containing the “silent installer” bash archive).  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script will request information about the version and installed path for the IBM SPSS app.
      - This information should be obtained by installing IBM SPSS on a test Mac first.
   * The *make-pkginfo.py* script will request IBM SPSS license information and other relevant details.
   * Some notes about the resulting pkginfo:
      - The resulting pkginfo will be a “copy from dmg” case with an *installs* array that differs from the *items_to_copy* array.  This *installs* array will be populated with the path to the SPSS app - the “end state.”  This array **won't** hold any path information for the *items_to_copy* (the “silent installer” bash archive in this case).  Recall that Munki relies on the *installs* array when determining if something has been installed already.<sup>1</sup>
      - The resulting pkginfo willhave a *requires* key set for a Java JVM according to script input..
      - If the version of SPSS is a fix patch, the *update_for* key will be set according to script input.
      - It will contain a postinstall script that writes */tmp/installer.properties* with the given license information.
      - The postinstall will call the bash archive and perform the installation, then clean up.
      - The postinstall includes logic to properly set the *DaemonHost* variable in *Contents/bin/spssprod.inf* inside the SPSS app bundle.  This information should have been read from the LSHOST variable in */tmp/installer.properties*.  This is a documented bug<sup>2</sup>.
      - The postinstall includes logic to remove *Contents/bin/lservrc* inside the SPSS app bundle, if present.  This file indicates a temporary license is being used.  It seems to be created by the silent installer by mistake, probably due to the aforementioned bug.
      - It will contain an uninstall script for removing the version of IBM SPSS.  The *uninstall_method* is set to *uninstall_script*.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - This script may need some slight modification after each new IBM SPSS release.

Deployment Method
----------
## Install SPSS on a Test Mac ##
1. Install SPSS on a test Mac system with the Munki tools installed.  For the test installation, you will need to make a sample *installer.properties* file.  Look at the example one provided in the IBM SPSS vendor disk image, or you can use the following as a template.  Refer to IBM's documentation if necessary<sup>2</sup>.  Due to a bug<sup>2</sup> in the SPSS installer, the software may be licensed as a trial.  That is OK for the test installation since all we care about is getting app metadata.
<pre>INSTALLER_UI=silent
LICENSE_ACCEPTED=true
network=1
InstallPython=1
LSHOST=hostname.of.license.server
COMMUTE_MAX_LIFE=7
COMPANYNAME=Your Organization
</pre>

2. After installation, have Munki figure out the version number by using *makepkginfo* like this:
   <pre>makepkginfo -f "/Applications/IBM/SPSS/Statistics/24/SPSSStatistics.app"</pre>
   * Look for the bundle version (*CFBundleShortVersionString*).  This is the version number that the *make-pkginfo.py* script will request.

## Add SPSS to the Repository ##
1. Copy the IBM SPSS Statistics disk image to the munki repository.  Use a good naming convention; for example: *IBM_SPSS_Statistics-version.dmg*, where *version* is the *CFBundleShortVersionString* number determined when you installed it on a test Mac.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The SPSS version
      - The path to the installed SPSS Statistics app, relative to the client
      - The path to the IBM SPSS Statistics disk image relative to the Munki repository's *pkgs* directory
      - The license server host name
      - The licensee
      - If the SPSS installer is an update (“patch fix”), then you can make it an *update_for* by specifying the name of the Munki item that it updates.  For example, *IBM_SPSS_Update-24.0.0.1* is an “update_for” *IBM_SPSS-24.0.0.0*.
      - The Munki item name for an Oracle Java JDK (example: *Oracle_Java_JDK*).  SPSS requires a Java JDK.
3. If the item is not an *update_for*, update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg IBM_SPSS_Statistics --section optional_installs --manifest common_optional_installs</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   - https://github.com/munki/munki/wiki/Pkginfo-Files
   - https://github.com/munki/munki/wiki/Supported-Pkginfo-Keys
   - https://github.com/munki/munki/wiki/How-Munki-Decides-What-Needs-To-Be-Installed
2. SPSS
   - Example *pkginfo*: https://groups.google.com/forum/#!topic/munki-dev/qySQdMNEItU
   - Silent Install Notes: https://developer.ibm.com/predictiveanalytics/2016/03/22/silent-installation-of-release-ibm-spss-statistics-24-on-macintosh/
   - APAR PI66924: http://www.ibm.com/support/entdocview.wss?uid=swg1PI66924
3. *sed* Examples: http://stackoverflow.com/questions/16440377/sed-replace-whole-line-when-match-found
