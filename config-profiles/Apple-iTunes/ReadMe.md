Apple iTunes - Disable Automatic iPod and iOS Device Sync
----------
The **make-mobileconfig-and-pkginfo.py** script generates an Apple configuration profile with a **com.apple.ManagedClient.preferences** payload holding forced (user-managed, system-managed) settings for the **com.apple.iTunes** domain.

The purpose is to disable automatic synchronization of mobile devices when they are connected.  It also prevents iTunes from opening automatically in those situations.
* **dontAutomaticallySyncIPods**: Sets this to true.

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, etc.
   - This script could be modified to add additional preference keys for iTunes.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - Your organization's prefix (e.g. *org.sample*)
      - A version for the configuration profile
      - A display name for your organization (e.g. *Some State University*)
      - The config profile's display name (e.g. *iTunes iOS Auto Sync Settings*)
      - The config profile's description (the line shown below the display name)
   * Profile and payload UUIDs are created dynamically. Payload identifiers are similarly programmatically generated strings using your organization's prefix.
2. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Apple_iTunes_Auto_iOS_Synchronization.mobileconfig --section managed_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/releases/tag/v2.2.0.2399
   * https://github.com/munki/munki/wiki/makepkginfo
2. Config Profile Reference
   * https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/Introduction/Introduction.html
   * https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/iPhoneConfigurationProfileRef.pdf
3. https://github.com/timsutton/mcxToProfile
4. Keys for _com.apple.iTunes_ discovered by inspection of _~/Library/Preferences/com.apple.iTunes.plist_ and https://gist.github.com/cgerke/237bc107f5141cfb4754
