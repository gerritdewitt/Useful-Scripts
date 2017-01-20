Safari HomePage Settings Profile
----------
The **make-mobileconfig-and-pkginfo.py** script generates an Apple configuration profile with a **com.apple.ManagedClient.preferences** payload holding Safari settings:
* **com.apple.Safari**: Sets these keys:
   - **HomePage**: the URL you specify
   - **NewWindowBehavior**: sets to zero (integer), meaning show the home page

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, etc.
   - This script could be modified to add new preference keys for Safari beyond just the home page.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - Your organization's prefix (e.g. *org.sample*)
      - A name identifier for the Safari settings (used purely for file naming and identification purposes, example: *classroom-safari*)
      - A version for the configuration profile
      - A display name for your organization (e.g. *Some State University*)
      - The config profile's display name (e.g. *Safari HomePage*)
      - The config profile's description (the line shown below the display name)
   * Profile and payload UUIDs are created dynamically. Payload identifiers are similarly programmatically generated strings using your organization's prefix.
2. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Apple_Safari.mobileconfig --section managed_installs --manifest some_manifest</pre>


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
4. Example Safari configuration profiles:
   * https://github.com/nmcspadden/Profiles/blob/master/Safari.mobileconfig
   * https://github.com/amsysuk/public_config_profiles/blob/master/First_Boot_Profiles/SafariHomepage.mobileconfig
