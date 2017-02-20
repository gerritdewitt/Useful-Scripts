Local Account Removal Automations
----------
The **make-pkginfo.py** script generates a “nopkg” Munki item that checks for and deletes a named local user account if the account exists, unless the time difference from when the nopkg item's *installcheck* runs to the account's creation timestamp is not more than seven an interval you specify.  Practically, this means that the account will be removed if:
   - the account exists, and creation timestamp is not available
   - the account exists, and the “days” part of the difference between now and the creation timestamp is more than the interval you specified. 

This item is run as a “nopkg” item in Munki, meaning that it only runs if systems can check-in.  Thus, systems off network will run the automation if and when they return.  It should be noted that the named local user may last for more than seven days in certain cases.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  It simply creates the Munki pkginfo for this nopkg item.
* Review and modify these scripts if account details change:
   - **installcheck.py**, the script that checks the configuration to determine if Munki should “install” the item (for a nopkg item, this would mean run the *preinstall.py* script).  This script contains the logic to determine if the named local user account should be deleted.
   - **preinstall.py**, the script that actually removes the account

Before You Begin
----------
Edit both the **installcheck.py** and **preinstall.py** files, adjusting these global variables:
   * Specify the name of the local user account that should be purged, if present, after a given period of time.
   * Specify the period of time for which the named local user account may be present.

Adding to Munki
----------
1. Run the *make-pkginfo.py* script and follow its prompts to generate the nopkg item's *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - A name for the Munki item (example: *Configuration_Remove_named_local_user*)
      - A version for the item
2. Unless you changed it, the nopkg item's pkginfo is named **Configuration_Remove_named_local_user-version** (where *named_local_user* and *version* are what you specified).
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Remove_named_local_user --section managed_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/wiki/makepkginfo
2. Account times measured from epoch:
   * http://www.epochconverter.com
   * https://discussions.apple.com/message/27705594#27705594
3. Python: time and date conversions
   * http://stackoverflow.com/questions/3694487/initialize-a-datetime-object-with-seconds-since-epoch
   * https://docs.python.org/2/library/datetime.html
4. *dscl*: https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/dscl.1.html
