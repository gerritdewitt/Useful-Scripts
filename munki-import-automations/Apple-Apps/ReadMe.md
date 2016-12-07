Packaging Apple Apps Distributed via the Mac App Store
----------
Scripts and notes for deploying Apple Apps distributed via the Mac App Store.

Licensing Notes
----------
Always make sure you have sufficient licenses for the apps you are deploying.  Nothing in this document should be construed as a means to circumvent purchasing licenses for apps!

## Hardware Bundle Licenses ##
There are five apps delivered via Apple Hardware Bundle licenses:  iMovie, GarageBand, Pages, Numbers, and Keynote.  Starting with the release of OS X 10.9 Mavericks, Apple made these apps available to newly shipping Mac systems at no additional charge<sup>2</sup>.  Hence, systems shipping after October 22, 2013 should have Hardware Bundle licenses for them.

These apps are available via the Mac App Store and its volume purchase program (VPP).

If you use Munki to deploy these apps, consider deploying them as conditional optional installs.  For example, you could use our **system_hw_bundle_oct_2013** condition which simply returns true or false based on the date of manufacture as determined by the system serial number.  An example optional install using this condition would involve adding a block like the following to the appropriate manifest(s)<sup>1</sup>:
<pre>
&lt;key>conditional_items&lt;/key>
&lt;array&gt;
&lt;dict&gt;
&lt;key&gt;condition&lt;/key&gt;
&lt;string&gt;system_hw_bundle_oct_2013 == TRUE&lt;/string&gt;
&lt;key&gt;optional_installs&lt;/key&gt;
&lt;array&gt;
&lt;string&gt;Apple_Pages&lt;/string&gt;
&lt;string&gt;Apple_Numbers&lt;/string&gt;
&lt;string&gt;Apple_Keynote&lt;/string&gt;
&lt;string&gt;Apple_iMovie&lt;/string&gt;
&lt;string&gt;Apple_GarageBand&lt;/string&gt;
&lt;/array&gt;
&lt;/dict&gt;
&lt;/array&gt;
</pre>

## Deploying iMovie, Garageband, Pages, Numbers, and Keynote as Managed Installs ##
If deploying these apps via managed installs is more appropriate - in a computer lab, for instance - you need to make sure that all computers receiving them have licenses.  The licenses could be from various sources:
   * Hardware Bundle Licenses, if the serial numbers of the computers indicate they were made on or after October 23, 2013.
   * VPP Licenses could be procured via the Apple Volume Purchase Program to cover systems that don't have Hardware Bundle Licenses.

## Deploying Pay-For Apps ##
Generally speaking, other Apple apps must be purchased.  Licenses for Final Cut Pro, Motion, Compressor, Logic, and MainStage are available via VPP Licenses or annual subscription licenses (AELP, education customers only).

Deployment Overview
----------
1. The Installer package for the app will need to be captured from the Mac App Store.
2. The captured package should be installed on a test Mac to make sure the app installs and functions properly.
3. We'll programmatically create a *pkginfo* file for the captured “pkg”.  The *make-pkginfo.py* script serves this purpose.
   - The *make-pkginfo.py* script is interactive, and will ask for information required to generate the *pkginfo* metadata.

## About Capturing Packages ##
Anything from the Mac App Store distributed via Munki must be “captured”; for deployment because Apple doesn't (yet) offer a means for acquiring the installer packages easily.

There's plenty of information about how to capture the packages from the App Store's cache folder online, but some of those suggestions (such as unloading *installd*) won't work in macOS 10.11 and later due to SIP.<sup>4</sup>

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
* Capturing installer packages from the Mac App Store obviously requires a Mac running the current macOS.
* You'll need an Apple ID for redeeming purchased apps.  It's a good idea to have a non-person Apple ID owned and controlled by your institution for this purpose.
   - You'll need to have purchased or otherwise redeemed the app you need to deploy so that it shows up in the purchase history for that Apple ID.

Deployment Method
----------
## Capture Package from App Store ##
On a test or administrative Mac system: 
1. Open the App Store.  Sign in using the appropriate Apple ID.
2. If the app is already installed, delete it.  We do this so the App Store will let us download it again, and so we get the current and complete pkg from Apple. 
   - For **example**:
   - <pre>sudo rm -rf /Applications/Keynote.app</pre>
3. Check the **Purchases** and **Updates** tabs to be sure that no app downloads are in progress, and that none are paused.
   - This technique is meant to download and capture installer packages serially.
4. Locate the app in the **Purchases** tab, and start downloading it.  Wait until some data has been received, then press the **Pause** button.
   - Don't let the App Store get to the “installing” phase.
5. Determine the location of the download folder.  It's somewhere in **/private/var/folders**. Earlier versions of macOS had a “debug menu” for the App Store<sup>3</sup>, but that feature appears to be missing in macOS Sierra. You can still find the app's download path by doing the following.
   - Find the location of the downloads folder by running this search for *pfpkg* files in */private/var/folders*:
   - <pre>pf_package_path=$(find /private/var/folders -name *.pfpkg)</pre>
   - Verify that the **pf_package_path** exists (and is not a list of paths).  You can do this quickly with *ls*:
   - <pre>ls "$pf_package_path" # You should see one path, ending in .pfpkg </pre>
   - Provided you have a single *.pfpkg* path, get the *actual package path* from its parent directory:
   - <pre>parent_dir=$(dirname "$pf_package_path")</pre>
   - <pre>package_path=$(find "$parent_dir" -name \*.pkg)</pre>
   - Verify that the **package_path** exists (and is not a list of paths).  Again, with *ls*:
   - <pre>ls "$package_path" # You should see one path, ending in .pkg </pre>
   - An App Store **package_path** looks like this: */private/var/folders/j7/h60wxfp15c74y0kkcthtnrpr4y0r3l/C/com.apple.appstore/424389933/bqa1145527233661137693.pkg*
6. Create *another* hard link for the package being downloaded; for **example**:
   - <pre>ln "$package_path" /tmp/keynote.pkg</pre>
7. Return to App Store and press the **Resume** button.
   - Let App Store finish downloading and installing.
   - After installation, the other hard link for the package will be retained, even though the one in */private/var/folders* will be removed.

## Test Install Captured Package ##
The goal here is to verify that you have captured a valid installer package.
1. Delete the app as installed by the App Store; for **example**:
<pre>sudo rm -rf /Applications/Keynote.app</pre>
2. Install the captured package.  You can do this quickly with *installer*.  Using our **example**:
<pre>installer -verbose -target / -pkg /tmp/keynote.pkg</pre>
3. Verify that the app installs successfully.  Test it out.

## Add App to the Repository ##
1. Once the captured package is validated, copy it to the **pkgs** directory in your Munki repository.  The pkg itself needs no modification.
   - Use a good naming convention; for example: *Apple_Keynote-version.pkg*.
   - By not modifying the captured package, you are preserving its code signature and proof of integrity.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The app pkg name (example: **Apple_Keynote**)
      - The display name (example: **Apple Keynote**)
      - The app version.  Use the version as displayed in the App Store.
      - The minimal version of macOS required by the app.  Refer to the notes Apple provides in the App Store.
      - The path to the installed app relative to the client (example: **/Applications/Apple Pages.app**).
      - The path to the captured installer package relative to the Munki repository's pkgs directory.
3. Update catalogs, and add the software to the appropriate manifest(s).  You could use the conditional optional installs example given above.

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   - https://github.com/munki/munki/wiki/Pkginfo-Files
   - https://github.com/munki/munki/wiki/Supported-Pkginfo-Keys
   - https://github.com/munki/munki/wiki/Conditional-Items
   - https://github.com/timsutton/munki-conditions
2. Apple Introduces Next Generation iWork and iLife Apps for OS X and iOS: https://www.apple.com/pr/library/2013/10/23Apple-Introduces-Next-Generation-iWork-and-iLife-Apps-for-OS-X-and-iOS.html
3. Enable the Debug Menu in the Mac App Store: http://krypted.com/mac-os-x/enable-the-debug-menu-in-the-mac-app-store/
4. Capturing Packages from the App Store:
   - http://pivotallabs.com/accessing-the-packages-that-underlie-apple-s-app-store/
   - https://jonbrown.org/blog/10-9-deploying-appstore-packages/
   - https://derflounder.wordpress.com/2013/08/22/downloading-apples-server-app-installer-package/

