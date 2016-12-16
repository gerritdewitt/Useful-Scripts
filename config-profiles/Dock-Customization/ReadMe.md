Dock Configuration Profile
----------
The *make-mobileconfig-and-pkginfo.py* script generates an Apple configuration profile with a **com.apple.ManagedClient.preferences** payload containing Dock settings from a **com.apple.dock.plist** you specify.

A Dock configuration profile is a useful way to set the contents of the Dock based on template you configure.  You may use this to provide a consistent Dock for a lab or classroom environment.

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.

Deployment Method
----------
1. Create a custom Dock on a sample computer.  Copy the *~/Library/Preferences/com.apple.dock.plist* file after you are happy with your configuration.
   * For best results, log out and back in to make sure the settings for the Dock are written to the *com.apple.dock.plist* file.
      - You could also simply *killall Dock* and verify your customizations are saved.
2. Hand-edit the *com.apple.dock.plist* file as necessary.  For example, you should replace absolute paths to items in user home directories (for directory tiles) with “home directory relative” items.
3. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the configuration profile and its *pkginfo* file.  For example:
<pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - Your organization's prefix (example: *org.sample*), if that is not set as a shell environment variable
      - A name identifier for the Dock (used purely for file naming and identification purposes, example: *classroom-dock*)
      - A version for the configuration profile (example: *2016.10*)
      - Your organization's display name (example: *Some State University*)
      - A profile display name (example: *Dock Settings*)
      - A profile description (example: *From the IT Department*)

4. Update catalogs and add the profile to the appropriate manifest(s); for *example*:
<pre>makecatalogs</pre>
<pre>manifestutil --add-pkg Configuration_Setup_Assistant.mobileconfig --section managed_installs --manifest some_manifest</pre>

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
3. MCX to Profile
   - https://github.com/timsutton/mcxToProfile
