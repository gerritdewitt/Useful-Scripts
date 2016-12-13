McAfee Agent Materials
----------
Scripts and notes for deploying the McAfee Agent with Munki.

## Challenges to Deployment ##
The McAfee Agent is distributed as a bash archive (or a zipped version thereof)<sup>2</sup>.  Using proper macOS terminology, the McAfee Agent is actually a *daemon*, because it is loaded by launchd in the system context, runs as root, and has no UI.  It also seems that the terms “McAfee Agent,” “McAfee EPO Agent,” “EPO Agent,” “ma,” and “cma” are synonymous.

1. **Install the Installer Problem**: Creating the *pkginfo* for this item requires knowing about Munki's “copy from dmg” installation method, and a solid understanding of how Munki determines if something is installed.<sup>1</sup>  We'll need a postinstall script to run the bash archive like this:
   - <pre>sudo install.sh -i</pre>

2. **Agent Installer Failure Cases**:  There are some cases where the installer will fail, though.  For smoothest deployment, we've found:
   - It's best to uninstall all previous McAfee products.
   - Uninstall scripts for previous versions are provided with those installations<sup>2</sup>:
   - <pre>/Library/McAfee/agent/scripts/uninstall.sh #Agent 5.x</pre>
   - <pre>/Library/McAfee/cma/uninstall.sh #Agent 4.x</pre>
   - The entire */Library/McAfee* folder must be removed or the installer bash archive will fail.  We discovered this though experimentation.

## Deployment Overview ##
A simple deployment strategy for the Agent is as follows.  After the Agent is deplyed, it communicates with its server to download and install other McAfee components, such as firewall or threat protection services.

1. Create a disk image containing the McAfee Agent bash archive (typically named *install.sh*).  Add that disk image to the Munki repository.
2. Programmatically create a *pkginfo* file for the “pkg” (the disk image containing bash archive).
   - The resulting *pkginfo* will contain an **installcheck script** that reads various McAfee XML files to determine what version of the Agent, if any, is installed.  This installcheck script has a higher priority than an installs array, and its return code will be the sole determiner as to whether or not the current Agent is installed.
   - The resulting pkginfo will contain an **postinstall script** that removes any previous McAfee product and runs the McAfee Agent bash archive.

The *make-pkg-and-pkginfo.py* script performs both of these tasks.  Specifically: 
   * The *make-pkg-and-pkginfo.py* script will request information about the version and a path to the McAfee Agent bash archive.
   * It will create a UDZO disk image containing the McAfee Agent bash archive.
   * It will create the *pkginfo* as described above.

Before You Begin
----------
* Review and modify the *make-pkg-and-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.
   - This script may need some slight modification after each new McAfee Agent release.

Deployment Method
----------
## Install McAfee Agent on a Test Mac ##
1. On a test Mac system, install the Agent manually by running its bash archive:
<pre>sudo install.sh -i</pre>

2. Verify that the Agent is installed and working properly.  Other McAfee components should be delivered to the client computer after the Agent is able to communicate with its server.

3. Determine the version of the installed Agent: how?

## Add McAfee Agent to the Repository ##
1. Run the *make-pkg-and-pkginfo.py* script and follow its prompts to generate the disk image and *pkginfo* file.  For example:
   <pre>./make-pkg-and-pkginfo.py</pre>
   * The script is interactive.  It will ask for:
      - The base path to the Munki repo, if that is not set as a shell environment variable
      - The version of the McAfee Agent
      - The path to the McAfee Agent bash archive, *install.sh*.  This item will be copied into a disk image, which will be copied to your Munki repository.
3. Update catalogs, and add the software to the appropriate manifest(s); for *example*:
   <pre>makecatalogs</pre>
   <pre>manifestutil --add-pkg McAfee_Agent --section managed_installs --manifest some_manifest</pre>

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
2. McAfee
   - McAfee ePO for OS X: https://www.nbalonso.com/mcafee-epo-for-os-x/
   - How to uninstall and re-install McAfee Agent 4.x on Macintosh computers: https://kc.mcafee.com/corporate/index?page=content&id=KB61125
3. Misc
   - https://docs.python.org/2/library/shutil.html
   - https://docs.python.org/2/library/xml.etree.elementtree.html
   - http://stackoverflow.com/questions/11887762/compare-version-strings
