Maplesoft Maple Materials
----------
Scripts and notes for deploying Maple with Munki.

## Challenges to Deployment ##
Maplesoft provides a means for performing a silent installation, serialization, and activation of Maple using a custom app. For this case, it's best for Munki to install the vendor's “installer” app, then run it via postinstall script.

1. **Licensing**: For silent licensing and activation, the vendor's installer app expects to be fed a path to an **installer properties file** which contains license information, including type, address of the license server, etc.  Fortunately, this format is rather straightforward, and is documented by Maplesoft.<sup>2</sup>
   - Our *make-pkginfo.py* script generates a very simple *installer.properties* file “from scratch” using information it collects when run.

2. **Install the Installer Problem**: Creating the *pkginfo* for this item requires knowing about Munki's “copy from dmg” installation method, and a solid understanding of how Munki determines if something is installed.  Uninstallation must also be considered, since *remove_copied_items* makes no sense for an “install the installer” case.<sup>1</sup>

## Deployment Overview ##
1. The Maplesoft Maple disk image should be copied to the Munki repository.  No changes are necessary to the disk image.
2. We'll programmatically create a *pkginfo* file for the “pkg” (the disk image containing vendor's installer - named something like *Maple2016.1MacInstaller.app*).  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script will request information about the version and installed path for the Maple app.
      - This information should be obtained by installing Maple on a test Mac first.
   * The *make-pkginfo.py* script will request license information and other relevant details.
   * Some notes about the resulting pkginfo:
      - The resulting pkginfo will be a “copy from dmg” case with an *installs* array that differs from the *items_to_copy* array.  This *installs* array will be populated with the path to the Maple app - the “end state.”  This array **won't** hold any path information for the *items_to_copy* (the vendor's installer).  Recall that Munki relies on the *installs* array when determining if something has been installed already.<sup>1</sup>
      - It will contain a postinstall script that writes */tmp/maple_installer.properties* with the given license information.
      - The postinstall will call the vendor's custom installer app to perform the installation, then clean up.
      - It will contain an uninstall script for removing the version of Maple.  The *uninstall_method* is set to *uninstall_script*.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - This script may need some slight modification after each new Maple release.

Deployment Method
----------
## Install Maple on a Test Mac ##
1. Install Maple on a test Mac system with the Munki tools installed.  For the test installation, simply manually run the vendor's custom installer app (example: *Maple2016.1MacInstaller.app*) and supply information for network licensing interactively.

2. After installation, have Munki figure out the version number by using *makepkginfo* like this:
   <pre>makepkginfo -f "/Applications/Maple 2016/Maple 2016.app"</pre>
   * Look for the bundle version (*CFBundleShortVersionString*).  This is the version number that the *make-pkginfo.py* script will request.

## Add Maple to the Repository ##
1. Copy the Maplesoft Maple disk image to the munki repository.  Use a good naming convention; for example: *Maplesoft_Maple-version.dmg*, where *version* is the *CFBundleShortVersionString* number determined when you installed it on a test Mac.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The Maple version
      - The path to the installed Maplesoft Maple app, relative to the client
      - The path to the Maplesoft Maple disk image relative to the Munki repository's *pkgs* directory
      - The license server host name
3. Update catalogs.  Add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Maplesoft_Maple --section optional_installs --manifest some_manifest</pre>

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
2. Maple
   - Silent Install Notes: http://www.maplesoft.com/support/install/maple2015_install.html
