App Store Settings Configuration Profile
----------
The **make-mobileconfig-and-pkginfo.py** script generates an Apple configuration profile with a **com.apple.appstore** payload holding settings suitable for a lab or classroom environment. The default Mac App Store behavior in macOS 10.7 and later lets any user (not just a local admin) install apps (some requiring an Apple ID). This profile configures the App Store to require that the user be a local admin in order to install apps from there. It also disables a number of alerts, including update messages and offers to associate a hardware bundle with an individual's Apple ID.
* **restrict-store-require-admin-to-install**: true: Only local admins may install software offered in the Mac App Store.
* **restrict-store-disable-app-adoption**: true: Users will not be notified to “adopt” hardware bundle apps if they are not installed.  In a lab, such adoption could have the negative consequence of associating the lab computer's hardware bundle licenses with the Apple ID of a student!
* **restrict-store-softwareupdate-only**: true: This effectively disables the store functionality of App Store, leaving only the capability to install updates (subject to other settings).
* **DisableSoftwareUpdateNotifications**: true: App Store will not use Notification Center to announce available updates.

If you use this profile, it's a good idea to have some kind of automatic software update mechanism in place; for example, if you use Munki, let it install Apple Software Updates, or use a configuration profile to turn on automatic Software Updates.  Don't configure your lab or classroom to not update itself!
   
Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, etc.
   - This script could be modified to add new preference keys for App Store if Apple adds new features.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - Your organization's prefix (e.g. *org.sample*)
      - A version for the configuration profile
      - A display name for your organization (e.g. *Some State University*)
      - The config profile's display name (e.g. *App Store Settings*)
      - The config profile's description (the line shown below the display name)
   * Profile and payload UUIDs are created dynamically. Payload identifiers are similarly programmatically generated strings using your organization's prefix.
2. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Apple_App_Store.mobileconfig --section managed_installs --manifest some_manifest</pre>


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
   * https://developer.apple.com/library/prerelease/content/featuredarticles/iPhoneConfigurationProfileRef/Introduction/Introduction.html
3. https://github.com/timsutton/mcxToProfile
4. Example App Store configuration profiles:
   * https://github.com/nmcspadden/Profiles/blob/master/AppStoreAdmin.mobileconfig
   * https://mosen.github.io/profiledocs/payloads/appstore.html
