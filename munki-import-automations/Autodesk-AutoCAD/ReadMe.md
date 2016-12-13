Autodesk AutoCAD Materials
----------
Scripts and notes for deploying Autodesk AutoCAD with Munki.

## Challenges to Deployment ##
AutoCAD is distributed on a disk image with an Apple pkg inside.  But there are some challenges to its deployment:

1. **Licensing**: When the installed app is run, it expects to find license information in a “licpath.lic” file which the vendor recommends deploying inside the app wrapper (*/Applications/Autodesk/AutoCAD 2016/AutoCAD.app/Contents/licpath.lic* for example).<sup>2</sup>  Unfortunately, testing proves this technique does not work for AutoCAD 2016.
   * Watching an AutoCAD 2016 installation, it's obvious that the vendor uses a custom Installer plugin to write a temporary file to */tmp/acodeAutoCAD2016*.  This file contains product key, serial, and license server information in a special format.<sup>2</sup>  This only works if installing in an interactive fashion, not via a command-line installation environment.

2. **Dock Icon**: Since we're installing in a command line environment, the package for adding the icon to the Dock is not reliable.  It must be disabled so that the command-line installation works.

## Deployment Overview ##
1. The Autodesk AutoCAD disk image should be copied to the Munki repository.  No changes are necessary to the disk image.
2. We'll programmatically create a *pkginfo* file for the “pkg” (the disk image containing the pkg - the Autodesk AutoCAD disk image).  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script will request information about the version and installed path for the AutoCAD app.
      - This information should be obtained by installing AutoCAD on a test Mac first.
   * The *make-pkginfo.py* script will request AutoCAD license information.  
      - The resulting pkginfo will contain a preinstall script that writes */tmp/acodeAutoCAD2016* with the given license information.
   * The *make-pkginfo.py* script will request a *choice changes XML file*.
      - This is the file that turns off the package for adding the AutoCAD icon to the Dock.
      - The choice changes XML file needs to be generated separately.  The *make-pkginfo.py* script will request the path to a pre-generated choice changes XML file.  This repository includes a sample choice changes file for Autodesk AutoCAD 2016.
      - Documentation about how to generate choice changes is here: https://github.com/munki/munki/wiki/ChoiceChangesXML

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - This script will need some slight modification after each new AutoCAD release.

Deployment Method
----------
## Install AutoCAD on a Test Mac ##
1. Install Autodesk AutoCAD on a test Mac system with the Munki tools installed.  You can choose to license the software as a trial; what's important is that it gets installed temporarily so you can measure the product's version number.
2. After installation, have Munki figure out the version number by using *makepkginfo* like this:
   <pre> makepkginfo -f "/Applications/Autodesk/AutoCAD 2016/AutoCAD 2016.app"</pre>
   * Look for the bundle version (*CFBundleVersion*).  This is the version number that the *make-pkginfo.py* script will request.

## Add AutoCAD to the Repository ##
1. Copy the Autodesk AutoCAD disk image to the munki repository.  Use a good naming convention; for example: *Autodesk_AutoCAD-version.dmg*, where *version* is the *CFBundleVersion* number determined when you installed AutoCAD on a test Mac.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The AutoCAD version
      - The path to the installed AutoCAD app, relative to the client
      - The path to the Autodesk AutoCAD disk image relative to the Munki repository's *pkgs* directory
      - The AutoCAD serial and product key
      - The license server host name
      - The path to the installer choice changes XML file.  The included *choice_changes-AutoCAD-2016.plist* file works for AutoCAD 2016.
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Autodesk_AutoCAD --section optional_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/wiki/Pkginfo-Files
   * https://github.com/munki/munki/wiki/Supported-Pkginfo-Keys
   * https://github.com/munki/munki/wiki/ChoiceChangesXML
2. Autodesk
   * https://knowledge.autodesk.com/support/vault-products/troubleshooting/caas/sfdcarticles/sfdcarticles/Does-the-MAC-installer-for-Autodesk-Alias-2014-support-the-Redundant-License-Server.html
   * http://forums.autodesk.com/t5/autocad-for-mac-forum/deploying-autocad-2014-for-mac-to-computer-labs/td-p/5032058
