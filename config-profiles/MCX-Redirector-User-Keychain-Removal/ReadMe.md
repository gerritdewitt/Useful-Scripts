MCX Redirector Profile: User Keychain Removal
----------
The **make-mobileconfig-and-pkginfo.py** script generates an Apple configuration profile with a **com.apple.ManagedClient.preferences** payload holding MCX folder redirection settings to delete **~/Library/Keychains** when users log out:
* **com.apple.MCXRedirector**: Sets these keys:
   - **LogoutRedirection**: array containing a single dictionary with keys:
      - **action**: *deletePath*
      - **path**: *~/Library/Keychains*

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, etc.
   - This script could be modified to add more MCX folder redirection settings. Refer to the *Sources* section at the end for inspiration.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - Your organization's prefix (e.g. *org.sample*)
      - A version for the configuration profile
      - A display name for your organization (e.g. *Some State University*)
      - The config profile's display name (e.g. *User Keychain Removal at Logout*)
      - The config profile's description (the line shown below the display name)
   * Profile and payload UUIDs are created dynamically. Payload identifiers are similarly programmatically generated strings using your organization's prefix.
2. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_MCX_Redirector_User_Keychain_Removal_Logout.mobileconfig --section managed_installs --manifest some_manifest</pre>


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
4. MCXRedirector Examples:
   * https://mosen.github.io/profiledocs/payloads/mcxredirector.html
   * http://simonmerrick.co.uk/blog/wp-content/uploads/2014/11/Screen-Shot-2014-11-25-at-10.05.34.png
