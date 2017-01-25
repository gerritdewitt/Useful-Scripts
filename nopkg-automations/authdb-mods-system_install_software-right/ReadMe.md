Authorization Database Modifications: Allow Installation of Software By All Users
----------
The **make-pkginfo.py** script generates a “nopkg” Munki item that modifies the authorization database referenced by *securityd* so that any user may install software via the Installer app.  This example may be useful for checkout laptops where it's undesirable to grant users full admin rights, but where they need some room to experiment by installing software.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  It simply creates the Munki pkginfo for this nopkg item.
* Review and modify these scripts if you wish to adjust the various authorization database modifications:
   - **installcheck.py**, the script that checks the configuration to determine if Munki should “install” the item (for a nopkg item, this would mean run the *preinstall.py* script).
   - **preinstall.py**, the script that actually makes the changes

Adding to Munki
----------
1. Run the *make-pkginfo.py* script and follow its prompts to generate the nopkg item's *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - A version for the item
2. Unless you changed it, the nopkg item's pkginfo is named **Configuration_Install_Software_All_Session_Users-version** (where *version* is what you specified).
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Install_Software_All_Session_Users --section managed_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/wiki/makepkginfo
2. Authorization Policy Database Manipulation
   * https://developer.apple.com/library/mac/technotes/tn2095/_index.html#//apple_ref/doc/uid/DTS10003110-CH1-SECTION6
   * https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man1/security.1.html
   * https://derflounder.wordpress.com/2014/02/16/managing-the-authorization-database-in-os-x-mavericks/
3. Specific Example Using Munki
   * https://grahamgilbert.com/blog/2013/12/22/managing-the-authorization-database-with-munki/
