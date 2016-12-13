Setup Assistant Offers Suppression Profile
----------
The *make-mobileconfig-and-pkginfo.py* script generates an Apple configuration profile with a **com.apple.SetupAssistant.managed** payload to disable various offers at log in, including ones for iCloud and Siri.

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.

Deployment Method
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the configuration profile and its *pkginfo* file.  For example:
<pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - Your organization's prefix (example: *org.sample*), if that is not set as a shell environment variable
      - A version for the configuration profile (example: *2016.10*)
      - Your organization's display name (example: *Some State University*)
      - A profile display name (example: *Setup Assistant Management*)
      - A profile description (example: *From the IT Department*)

2. Update catalogs and add the profile to the appropriate manifest(s); for *example*:
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
3. Setup Assistant Profile and Keys
   - Sourced from a sample profile taken from Profile Manager in Server.app 5.x
   - Some keys inferred from reading *com.apple.SetupAssistant* defaults for an already-configured account.
   - Skip Siri: https://github.com/rtrouton/profiles/blob/master/SkipSiriSetup/SkipSiriSetup.mobileconfig
