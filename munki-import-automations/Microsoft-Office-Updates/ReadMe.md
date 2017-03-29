Deploying Microsoft Apps with Munki
----------
Scripts and notes for deploying various Microsoft apps and updates via Munki, including:
* Office 2016 Updates
* Office 2011 Updates
* Skype for Business or Lync
* AutoUpdate

## Challenges to Deployment ##
Microsoft uses Apple package (pkg) installers for its products; some are are distributed as packages wrapped in disk image (dmg) files.  Munki can handle both correctly.

1. **Licensing**: Licensing is handled via Microsoft KMS.  For Office 2016, at least version 15.13.4 is required.  Earlier versions of Office 2011 had some major problems as well.<sup>3</sup>

2. **Receipt Data Unreliable**: All of the Microsoft Office installers and updaters we have encountered so far require the addition of an **installs** array to their *pkginfo* since relying on Apple receipt data is unreliable.  Failure to include an “installs” array can result in Munki to repeatedly offering or installing the apps.<sup>1,2</sup>

## Deployment Overview ##
1. The Microsoft app or Office update should be copied to the Munki repository.  No changes are necessary to the Installer package (pkg) or wrapping disk image (dmg).
2. We'll programmatically create a *pkginfo* file.  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script is interactive.  It can create pkginfo for Office 2016 updates (individual apps), Office 2011 suite updates, and other Microsoft app products.
   * Some notes about the resulting *pkginfo*:
      - It will be a standard Apple installer pkg case, but will include an *installs* array since receipt data may be unreliable.<sup>3</sup>  Installs arrays are created automatically for Office update cases; for other cases, the script will request the path to the installed app.
      - If the item is an Office 2011 or 2016 update, the *update_for* key will be set.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - Pay special attention to the names of the Microsoft Office 2016 and 2011 office suites.  We use naming conventions like *Microsoft_Office_2011* and *Microsoft_Office_2016*, where “2011” and “2016” are considered parts of the names of the items instead of version numbers.  (Proper version numbers are 14.x and 15.x respectively.)

Deployment Method
----------
## Test Installation ##
Consider manually installing the Office update or app on a test Mac system with the Munki tools installed so you can at least determine the *CFBundleShortVersionString*.  Microsoft is pretty consistent about how it sets the *CFBundleShortVersionString*, but recent Office 2016 updates have been appending what looks like a build date to the version number in the file name.  For example, the file version may be 15.29.16121500, but the *CFBundleShortVersionString* may be 15.29.1.

As an example, you can ask Munki the version number of an installed Office app by using *makepkginfo* like this:
   <pre>makepkginfo -f "/Applications/Microsoft Word.app"</pre>
   * Look for the bundle version (*CFBundleShortVersionString*).  This is the version number that the *make-pkginfo.py* script will request.

## Add Item to the Repository ##
1. Copy the Installer pkg or disk image (containing the installer pkg) to the munki repository.  Use a good naming convention; for example: *Microsoft_Office_2011_Update-14.7.1.dmg* or *Microsoft_Office_2016_Word_Update-15.29.1.pkg*.  Here's where knowing the *CFBundleShortVersionString* is handy.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will first request the base path to the Munki repo, if that is not set as a shell environment variable.
   * It will ask what type of Microsoft item you're adding.  Choices are:
      - **2016**: for adding an update for an Office 2016 app pkg
      - **2011**: for adding an update for the Office 2011 suite
      - **mau**: for adding the Microsoft AutoUpdate app
      - **standalone**: for adding something else, like Skype, Lync, or AutoUpdate
   * It will ask for other details, depending on the type selection:
      - If you selected an Office 2016 update, the script requests the name of the app (example: **Word**)
      - If adding a standalone app, the script requests the name (example: **Microsoft_Lync**) and display name (example: **Microsoft Lync**) of the item.
      - The app or update version
      - The minimal version of macOS required by the app.  Refer to Microsoft release notes.
      - If adding a standalone app, the script requests the path to the installed app relative to the client (example: **/Applications/Skype for Business.app**).
      - The path to the item's pkg or disk image relative to the Munki repository's *pkgs* directory
      - Optionally, a due date for the item, in days measured from when the *pkginfo* is created (now).
3. Update catalogs, and add the software to the appropriate manifest(s).  Here are some *examples*:
   <pre>makecatalogs</pre>
   * A mandatory update:
   <pre>manifestutil --add-pkg Microsoft_Office_2011_Update --section managed_updates --manifest includes/common-managed_updates</pre>
   * An optional offering:
   <pre>manifestutil --add-pkg Microsoft_Skype_For_Business --section optional_installs --manifest includes/common-optional_installs</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   - https://github.com/munki/munki/wiki/Pkginfo-Files
   - https://github.com/munki/munki/wiki/Supported-Pkginfo-Keys
   - https://github.com/munki/munki/wiki/How-Munki-Decides-What-Needs-To-Be-Installed
2. Specific Notes for Microsoft Office:
   - Managed Software Updates: Application Deployment and Management with Munki, page 30: http://macadmins.psu.edu/wp-content/uploads/sites/1567/2012/11/PSUMAC303-Munki-Nate_Walck.pdf
3. KMS Licensing & Office for Mac:
   - Munki and Office 2016: https://github.com/munki/munki/wiki/Munki%20And%20Office%202016
   - Fixing Microsoft Office 2011 SP2 Volume Licensing: http://blog.michael.kuron-germany.de/tag/com-microsoft-office-licensing/

