Managed Desktop Picture Profile & Automations
----------
There are two components to deploying a managed desktop picture (custom wallpaper) via configuration profile:
* The profile itself, which specifies the path to a Desktop Picture file.
* The desktop picture file.

The *make-mobileconfig-and-pkginfo.py* script generates an Apple configuration profile with a **com.apple.desktop** payload to set the managed desktop picture to a PNG image at this path: */Library/Desktop Pictures/Managed Desktop Picture.png*

The resulting configuration profile can be used to set many different desktop pictures, so long as you deploy what you want to */Library/Desktop Pictures/Managed Desktop Picture.png*

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.

Deployment Method
----------
Deployment involves two steps:
* Creating the configuration profile to set the managed desktop picture.
* Creating each of the various managed desktop pictures you wish to deploy.

## Creating the Configuration Profile ##
The configuration profile needs only be created and added to your Munki repository *once*.  It may be used to set several managed desktop pictures, because the profile simply references a file by path (*/Library/Desktop Pictures/Managed Desktop Picture.png*).
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the configuration profile and its *pkginfo* file.  For example:
<pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - Your organization's prefix (example: *org.sample*), if that is not set as a shell environment variable
      - A version for the configuration profile (example: *2017.01*)
      - Your organization's display name (example: *Some State University*)
      - A profile display name (example: *Managed Desktop Picture*)
      - A profile description (example: *From the IT Department*)
   * The name of the configuration profile created is *Configuration_Desktop_Picture_Managed.mobileconfig*.

## Creating Managed Desktop Pictures ##
1. Convert your desktop picture to PNG format if required.  Use Preview, Photoshop, sips, etc. to convert it.  (macOS supports various image formats, but for the sake of simplicity, we chose to fix the format to PNG and the installed path to */Library/Desktop Pictures/Managed Desktop Picture.png*.)

2. Run the *make-desktop-pic-pkg-and-pkginfo.py* script and follow its prompts to generate a dmg containing the managed desktop picture (the “pkg”) and its *pkginfo* file.  For example:
<pre>./make-desktop-pic-pkg-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The full path to the PNG image you want to use as the managed desktop picture. (Do not escape spaces, etc. in the path.)
      - A short name, without spaces, to identify the picture. (example: *Math_Labs*)
      - A display name (example: *Math Labs*)
      - A version for the managed desktop picture (example: *2017.01*)
      - The name of the configuration profile that will set the desktop picture (*Configuration_Desktop_Picture_Managed.mobileconfig* is the name of the profile created above).
   * The short name, display name, and version will be used like this:
      - The short name and version are used for the disk image and *pkginfo* names:
         - The “pkg” name for our example would be: *Desktop_Picture_Math_Labs-2017.01.dmg*
         - The *pkginfo* for our example would be: *Desktop_Picture_Math_Labs-2017.01*
      - The display name is used in the *pkginfo*; for example, if you specify *Math Labs*, the display name will be *Desktop Picture (Math Labs)*.

3. Update catalogs and add the managed desktop picture to the appropriate manifest(s); for *example*:
<pre>makecatalogs</pre>
<pre>manifestutil --add-pkg Desktop_Picture_Math_Labs-2017.01 --section managed_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   - https://github.com/munki/munki/releases/tag/v2.2.0.2399
   - https://github.com/munki/munki/wiki/makepkginfo
2. Config Profile Reference
   - https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/Introduction/Introduction.html
   - https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/iPhoneConfigurationProfileRef.pdf
3. Desktop Picture Profile and Keys
   - https://github.com/gregneagle/profiles/blob/master/desktop_picture.mobileconfig
   - https://github.com/nmcspadden/Profiles/blob/master/DesktopPicture.mobileconfig
