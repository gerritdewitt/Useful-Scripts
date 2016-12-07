Microsoft Office Settings Profile
----------
The **make-mobileconfig-and-pkginfo.py** script generates an Apple configuration profile with a **com.apple.ManagedClient.preferences** payload holding these settings:
* **com.microsoft.autoupdate2**: Sets this key:
   - **HowToCheck**: sets to the string “manual”
* **com.microsoft.error_reporting**: Sets these keys:
   -  **SQMReportsEnabled**: sets to false
   -  **ShipAssertEnabled**: sets to false
* **com.microsoft.office**: Sets these keys.  In conjunction with the keys in the **com.microsoft.error_reporting** preference, this prevents first run alerts.
   - **14\FirstRun\SetupComplete**: sets to true
   - **14\UserInfo\UserName**: sets to your organization's name (as requested by the *make-mobileconfig-and-pkginfo.py* script)
   - **14\UserInfo\UserOrganization** same as **14\UserInfo\UserName**
* **com.microsoft.Outlook** and **com.microsoft.onenote.mac**: Sets these keys:
   - **kSubUIAppCompletedFirstRunSetup1507**: sets to true to skip a first run window
   - **FirstRunExperienceCompletedO15**: sets to true to skip a first run window
   - **SendAllTelemetryEnabled**: sets to false to skip reporting of errors to Microsoft
* **com.microsoft.PowerPoint**, **com.microsoft.Excel**, and **com.microsoft.Word**: Sets these keys:
   - **kSubUIAppCompletedFirstRunSetup1507**: sets to true to skip a first run window
   - **SendAllTelemetryEnabled**: sets to false to skip reporting of errors to Microsoft

Before You Begin
----------
* Review and modify the *make-mobileconfig-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, etc.
   - This script will need modification to add new preference keys as new versions of Micrsoft Office apps are released.

Running the Script
----------
1. Run the *make-mobileconfig-and-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - Your organization's prefix (e.g. *org.sample*)
      - A version for the configuration profile.
      - A display name for your organization (e.g. *Some State University*)
      - The config profile's display name (e.g. *Microsoft Office Settings*)
      - The config profile's description (the line shown below the display name)
   * Profile and payload UUIDs are created dynamically. Payload identifiers are similarly programmatically generated strings using your organization's prefix.
2. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Microsoft_Office.mobileconfig --section managed_installs --manifest common_optional_installs</pre>


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
4. Office 2011 Prefs: http://www.officeformachelp.com/office/administration/mcx/
5. Office 2016 Prefs:
   * https://www.jamf.com/jamf-nation/discussions/18847/office-2016-diable-auto-updates
   * https://www.jamf.com/jamf-nation/discussions/19096/disabling-first-run-dialogs-in-office-2016-for-mac
   * https://derflounder.wordpress.com/2016/01/17/suppressing-office-2016s-first-run-dialog-windows/
   * https://osxbytes.wordpress.com/2015/09/17/not-much-whats-new-with-you/
