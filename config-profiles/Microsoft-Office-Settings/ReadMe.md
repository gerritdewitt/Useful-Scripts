Microsoft Office Settings Profile
----------
The _make-mobileconfig-and-pkginfo.py_ script generates an Apple configuration profile with a _com.apple.ManagedClient.preferences_ payload holding these settings:
* *com.microsoft.autoupdate2*: Sets the _HowToCheck_ key to &#8220;manual.&#8221;  Prevents update alerts.
* *com.microsoft.error_reporting*: Sets the _SQMReportsEnabled_ and _ShipAssertEnabled_ keys to false.  In conjunction with the keys in the _com.microsoft.office_ preference, this prevents first run alerts.
* *com.microsoft.office*: Sets the _14\FirstRun\SetupComplete_ key and fills in the _14\UserInfo\UserName_ and _14\UserInfo\UserOrganization_ keys with the string &#8220;GSU.&#8221;  In conjunction with the keys in the _com.microsoft.error_reporting_ preference, this prevents first run alerts.
* *com.microsoft.Outlook* and *com.microsoft.onenote.mac*: Sets these keys:
   * _kSubUIAppCompletedFirstRunSetup1507_: sets to true to skip a first run window
   * _FirstRunExperienceCompletedO15_: sets to true to skip a first run window
   * _SendAllTelemetryEnabled_: sets to false to skip reporting of errors to Microsoft
* *com.microsoft.PowerPoint*, *com.microsoft.Excel*, and *com.microsoft.Word*: Sets these keys:
   * _kSubUIAppCompletedFirstRunSetup1507_: sets to true to skip a first run window
   * _SendAllTelemetryEnabled_: sets to false to skip reporting of errors to Microsoft

Because this is an “admin script” designed to be run from an admin Mac, you may have to hand-edit various parameters in it whenever you need to generate an updated or modified profile.  The script itself has a good deal of inline documentation.

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
