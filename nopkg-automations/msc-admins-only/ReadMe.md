Managed Software Center - Admins Only Automations
----------
The **make-pkginfo.py** script generates a “nopkg” Munki item that sets permissions on Managed Software Center so that only admin users can open and use it. This has a side effect of suppressing MSC notifications for non-admin users, too. 

This item is run as a “nopkg” item in Munki, meaning that it only runs if systems can check-in.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  It simply creates the Munki pkginfo for this nopkg item.
* Review and modify these scripts if account details change:
   - **installcheck.py**, the script that checks the filesystem permissions on MSC to determine if Munki should “install” the item (for a nopkg item, this would mean run the *preinstall.py* script).
   - **preinstall.py**, the script that actually modifies the permissions for MSC
   - **uninstallcheck.py**, the script that sets permissions back to Munki defaults.  For strange reasons, with *nopkg* Munki items, experience with the tool (as of 2.8.2) indicates that only the *installcheck* script runs when doing an uninstall, even with *uninstall_method* set to *uninstall_script*.
   - **uninstall.sh**, this is a simple script that returns zero.  It seems that Munki does not actually run this, but we need to feed something into *makepkginfo*.

Adding to Munki
----------
1. Run the *make-pkginfo.py* script and follow its prompts to generate the nopkg item's *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - A version for the item
2. Unless you changed it, the nopkg item's pkginfo is named **Configuration_Managed_Software_Center_Admin_Only-version** (where *version* is what you specified).
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Managed_Software_Center_Admin_Only --section managed_installs --manifest some_manifest</pre>
4. Exemptions: Let's consider the case where every computer manifest nests a group manifest, and every group manifest nests an overall configuration manifest.  If *Configuration_Managed_Software_Center_Admin_Only* is a managed install in the overall configuration manifest, it can be “exempted” on a group or computer level by adding it to the managed uninstalls list of the group manifest or computer manifest.  In other words, the “closest” manifest to the computer “wins,” and managed uninstalls are processed with a higher priority than anything else.

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/wiki/makepkginfo
2. Python
   * https://docs.python.org/2/library/os.html
   * https://docs.python.org/2/library/stat.html
   * http://stackoverflow.com/questions/2853723/whats-the-python-way-for-recursively-setting-file-permissions
3. Interpreting POSIX mode from *stat*: https://stomp.colorado.edu/blog/blog/2010/10/22/on-python-stat-octal-and-file-system-permissions/
4. Examples:
   * http://stackoverflow.com/questions/5994840/how-to-change-the-user-and-group-permissions-for-a-directory-by-name
   * http://stackoverflow.com/questions/16249440/changing-file-permission-in-python
   * http://thomas-cokelaer.info/blog/2014/08/python-function-chmod-to-change-change-the-permission/
