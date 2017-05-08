Active Directory Binding Profile
----------
The *make-mobileconfig-and-pkginfo.py* script generates an Apple configuration profile with a **com.apple.DirectoryService.managed** payload with settings you specify for joining an AD domain.

The script also adds a **preinstall.py** script to the pkginfo it generates.  The preinsall script does the following:
   - It runs *ntpdate* to update the system clock against a time server specified in the script.
   - Removes the *DefaultKeychain* key from */Library/Preferences/com.apple.security.plist*, if present.  This forces macOS into using */Library/Keychains/System.keychain* as the system keychain, which is where it will write the computer record name and password.  Removing this key solves one frustratingly unspecific “cannot bind” problem in macOS.

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - Some AD specific settings are defined explicitly in the *payload_ad_dict*, which you may want to edit to suit your needs.
* Review the Munki Conditions, as installation of this profile should be handled as a conditional managed install based on the **ad_status** condition.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the configuration profile and its *pkginfo* file.  For example:
<pre>./make-mobileconfig-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - Your organization's prefix (example: *org.sample*), if that is not set as a shell environment variable
      - A version for the configuration profile (example: *2017.05*)
      - Your organization's display name (example: *Some State University*)
      - Some details about your AD configuration:
         - AD forest (example: *forest.sample.org*), which is purely informational (used to create the profile display name).  It may be the same as the domain for single domain forests.
         - AD domain to join (example: *dom.forest.sample.org*).  This is the host name the configuration file uses.
         - User name for binding, such as a service account name.  This is stored in plain text in the config file, but deleted after installation.
         - Password for binding user.  This is stored in plain text in the config file, but deleted after installation.
         - Default OU for new computers (example: *OU=Computers,DC=dom,DC=forest,DC=sample,DC=org*)
         - Comma separated list of AD groups to grant local admin rights (leave blank for none)
         - Your organization's NTP server (example: *ntp.sample.org*)
      - A profile description (example: *From the IT Department*)
2. Update catalogs; for *example*:
<pre>makecatalogs</pre>
3. Generally speaking, we offer the *Configuration_Active_Directory.mobileconfig* as a conditional managed install depending on our **ad_status** Munki condition.  Though you can't add conditional installs with *manifestutil*, you can add them manually.

You can use the **ad-status.py** Munki condition with a configuration profile to bind Mac systems to Active Directory.  If the **ad_status** is **on-network-unbound**, then a configuration profile for binding to AD may be offered as a managed install.  Here is an example block for placement in a group or upper-level included manifest:<pre>
&lt;key>conditional_items&lt;/key>
&lt;array&gt;
&lt;dict&gt;
&lt;key&gt;condition&lt;/key&gt;
&lt;string&gt;ad_status == "on-network-unbound"&lt;/string&gt;
&lt;key&gt;managed_installs&lt;/key&gt;
&lt;array&gt;
&lt;string&gt;Configuration_Active_Directory.mobileconfig&lt;/string&gt;
&lt;/array&gt;
&lt;/dict&gt;
&lt;/array&gt;
</pre>

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
   - https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/Introduction/Introduction.html#//apple_ref/doc/uid/TP40010206-CH1-SW30
   - https://developer.apple.com/library/ios/featuredarticles/iPhoneConfigurationProfileRef/iPhoneConfigurationProfileRef.pdf
3. Directory Profile and Keys
   - https://gist.github.com/scriptingosx/80ec4fc216dce8b1e4e3
   - https://support.apple.com/en-us/HT202834
4. Path to script: http://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
5. *ntpdate*: https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/ntpdate.8.html
