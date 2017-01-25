Wi-Fi Adapter Automations
----------
The **make-pkginfo.py** script generates a “nopkg” Munki item that checks for and enforces the following settings for Wi-Fi on Mac systems to which it is deployed: 
   - DisconnectOnLogout: no
   - JoinMode: automatic
   - RememberRecentNetworks: no
   - RequireAdminPowerToggle: yes

These settings are handy for “wireless only” labs & classrooms so that users aren't able to turn off the Wi-Fi interface on Mac systems.

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  It simply creates the Munki pkginfo for this nopkg item.
* Review and modify these scripts if you wish to adjust the various Wi-Fi parameters:
   - **installcheck.py**, the script that checks the configuration to determine if Munki should “install” the item (for a nopkg item, this would mean run the *preinstall.py* script).
   - **preinstall.py**, the script that actually does the configuration

Adding to Munki
----------
1. Run the *make-pkginfo.py* script and follow its prompts to generate the nopkg item's *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable.
      - A version for the item
2. Unless you changed it, the nopkg item's pkginfo is named **Configuration_Wi-Fi_Labs_Prefs-version** (where *version* is what you specified).
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg Configuration_Wi-Fi_Labs_Prefs --section managed_installs --manifest some_manifest</pre>

Author
----------
Written by Gerrit DeWitt (gdewitt@gsu.edu)
Copyright Georgia State University

Sources
----------
1. Munki
   * https://github.com/munki/munki/wiki/makepkginfo
2. Notes for airportd
   * http://osxdaily.com/2007/01/18/airport-the-little-known-command-line-wireless-utility/
   * https://discussions.apple.com/thread/7430732?start=0&tstart=0
   * usage notes for */usr/libexec/airportd*
3. Python: stderror to stdout with subprocess
   * http://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
