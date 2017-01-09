MathWorks MATLAB Materials
----------
Scripts and notes for deploying MathWorks MATLAB with Munki.

## Challenges to Deployment ##
MathWorks provides a means for performing a silent installation, serialization, and activation of MATLAB using its custom *InstallForMacOSX.app*.  For this case, it's best for Munki to install the vendor's “installer” app, then run it via postinstall script.

1. **Licensing**: The MATLAB installer expects to be fed a path to an **installer input file** which contains some control information, the file installation key, and the paths to two more files:
   - a **network license server file**:  this file holds the address to the license server, etc.  Fortunately, this format is rather straightforward, and there are examples and notes online.<sup>2</sup>
   - an **activation file**:  this file holds information about how to activate the product.  Unfortunately, MathWorks does not document the format for this file (at least not in their Mac downloads), but we found other sources online that do.<sup>2</sup>

2. **Install the Installer Problem**: Creating the *pkginfo* for this item requires knowing about Munki's “copy from dmg” installation method, and a solid understanding of how Munki determines if something is installed.  Uninstallation must also be considered, since *remove_copied_items* makes no sense for an “install the installer” case.<sup>1</sup>

## Deployment Overview ##
1. Downloaded the MathWorks MATLAB disk image (dmg).  Note that it's a read-write, uncompressed disk image, so it's not ideal for deployment until you convert it to read-only compresed.  You can do that easily via *hdiutil*:
<pre>hdiutil convert -format UDZO -o MathWorks_MATLAB_2016B-9.1.0.dmg matlab_R2016b_maci64.dmg</pre>
2. Copy the read-only, compressed MathWorks MATLAB disk image (dmg) to the Munki repository.
3. We'll programmatically create a *pkginfo* file for the “pkg” (the disk image containing the MathWorks installer).  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script will request information about the version and installed path for MathWorks MATLAB.
      - This information should be obtained by installing MathWorks MATLAB on a test Mac first.
   * The *make-pkginfo.py* script will request license information and other relevant details.
   * Some notes about the resulting pkginfo:
      - The resulting pkginfo will be a “copy from dmg” case with an *installs* array that differs from the *items_to_copy* array.  This *installs* array will be populated with the path to the MATLAB app - the “end state.”  This array **won't** hold any path information for the *items_to_copy*.  Recall that Munki relies on the *installs* array when determining if something has been installed already.<sup>1</sup>
         - The item copied is the *InstallForMacOSX.app* (the vendor's custom installer).
      - It will contain a postinstall script that:
         - writes the **installer input file** to */tmp/matlab_installer_input.txt*
         - writes the **network license server file** to */tmp/matlab_network.lic*
         - writes the **activation file** to */tmp/matlab_activation.ini*
         - calls the *InstallForMacOSX.app* to perform the installation
         - cleans up
      - It will contain an uninstall script for removing the installed version of MathWorks MATLAB.  The *uninstall_method* is set to *uninstall_script*.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - This script may need some slight modification after each new MathWorks MATLAB version.

Deployment Method
----------
## Install MATLAB on a Test Mac ##
1. Install MATLAB on a test Mac system with the Munki tools installed.  For the test installation, the application can be installed as a trial.  Thus, simply run the *InstallForMacOSX.app* and complete the process manually.
2. After installation, have Munki figure out the version number by using *makepkginfo* like this:
   <pre>makepkginfo -f "/Applications/MATLAB_R2016b.app"</pre>
   * Look for the bundle version (*CFBundleVersion*).  This is the version number that the *make-pkginfo.py* script will request.

## Add MATLAB to the Repository ##
1. Copy the MathWorks MATLAB disk image to the munki repository.  Use a good naming convention; for example: *MathWorks_MATLAB-version.dmg*, where *version* is the *CFBundleVersion* number determined when you installed it on a test Mac.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The MATLAB version as determined by installing it on the test system.  This is where knowing the *CFBundleVersion* is handy.
      - The path to the installed MATLAB app, relative to the client (example: **/Applications/MATLAB_R2016b.app**)
      - The path to the MATLAB disk image relative to the Munki repository's *pkgs* directory
      - The MATLAB file installation key
      - The license file string
3. Update catalogs.  Add the software to the appropriate manifest(s) if it is not an “update_for”; for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg MathWorks_MATLAB --section optional_installs --manifest some_manifest</pre>

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
2. MATLAB & Silent Installation with Activation
   - Example MATLAB Munki Import: https://github.com/grahampugh/osx-scripts/tree/master/matlab-munki
   - MathWorks (Quite Incomplete): Install Noninteractively (Silent Installation): http://www.mathworks.com/help/install/ug/install-noninteractively-silent-installation.html
   - http://www.mathworks.com/matlabcentral/answers/uploaded_files/43872/activate.txt
   - http://maithegeek.blogspot.com/2015/10/instsall-matlab-on-linux.html
   - https://github.com/purpleidea/puppet-matlab/blob/master/templates/installer_input.txt.erb
