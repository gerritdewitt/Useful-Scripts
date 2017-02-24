Deploying Oracle JRE & JDK with Munki
----------
Scripts and notes for deploying these Oracle items:
   - Oracle JRE with web plugin (**/Library/Internet Plug-Ins/JavaAppletPlugin.plugin**)
   - Oracle JDK with JRE (installed in **/Library/Java/JavaVirtualMachines**)

## Challenges to Deployment ##
Oracle distributes the web plugin JRE and the JDK each as an Apple installer pkg wrapped in a disk image.

1. **JRE Installer Package**: The disk image installer for the web plugin JRE wraps the **JavaAppletPlugin.pkg** package inside an app.  While this might make sense for consumer distribution, it means that we have to tell Munki the path to the Apple installer package relative to the mounted dmg container.  For example, you can see that the **JavaAppletPlugin.pkg** is located in the top-most app on the mounted dmg: **/Volumes/Java 8 Update 121/Java 8 Update 121.app/Contents/Resources/JavaAppletPlugin.pkg**
   - As you can see, one challenge here is that the relative path to the pkg in the dmg changes from version to version!
   - Fortunately, the JDK is just a plain pkg inside of a dmg.

2. **Receipt Data Unreliable**: Both the JRE and JDK packages produce receipts with unreliable data.  We have to use other means to determine if the version of the JRE or JDK is installed or if an update should be offered:
   - For the JRE, we use an **installs** array, looking at the **CFBundleVersion** key for this Internet Plug-In: **/Library/Internet Plug-Ins/JavaAppletPlugin.plugin**
   - For the JDK, we use an **installcheck_script** that calls **/usr/libexec/java_home -xml** to determine the latest installed JDK.  JVMs (from JDKs) are usually located at: **/Library/Java/JavaVirtualMachines/jdk&lt;VERSION&gt;.jdk**

## Deployment Overview ##
1. Download the JRE and JDKs from http://www.oracle.com/technetwork/java/javase/downloads/index.html.  If given an option, always choose the **dmg** installer.
2. Copy the disk images to the Munki repository.  No changes are necessary to the Installer package (pkg) or wrapping disk image (dmg).  You do need to choose a sane name that only uses dashes to separate the product name from its version (multiple dashes in file names confuse Munki).
3. We'll programmatically create a *pkginfo* file.  The *make-pkginfo.py* script serves this purpose.
   * The *make-pkginfo.py* script is interactive.  It can create pkginfo for both JRE and JDK installers.
   * Some notes about the resulting *pkginfo*:
      - It will be a standard Apple installer pkg case, but will include an *installs* array (JRE) or an *installcheck_script* (JDK).

Before You Begin
----------
* Review and modify the *make-pkginfo.py* script as necessary for your environment.  The script is easy to read, and there are some global variables that control names, descriptions, and other product metadata.

Deployment Method
----------
## Test Installation ##
Consider manually installing each item on a test Mac system with the Munki tools installed.

## Add Item to the Repository ##
1. Copy the JRE or JDK disk image (containing the installer pkg) to the munki repository.  Use a good naming convention; for example: *Oracle_Java_Plugin-8u121.dmg* or *Oracle_Java_JDK-8u121.pkg*.  The *make-pkginfo.py* script will determine the exact version number, so the filesystem name for the dmg can use a “human readable” version after the dash in its name (here, that's *8u121*).  Again, use only one dash per dmg name to separate the short name from the version.
2. Run the *make-pkginfo.py* script and follow its prompts to generate the *pkginfo* file.  For example:
   <pre>./make-pkginfo.py</pre>
   * The script is interactive.  It will first request the base path to the Munki repo, if that is not set as a shell environment variable.
   * It will ask what type of Oracle item you're adding.  Choices are:
      - **jre**: for the JRE browser plugin
      - **jdk**: for the JDK (the Java Development kit, complete with its own JRE)
   * It will ask for the path to the item's pkg or disk image relative to the Munki repository's *pkgs* directory
   * It will ask for the minimal version of macOS required.
   * Optionally, it will ask for a due date for the item, in days measured from when the *pkginfo* is created (now).
3. Update catalogs, and add the software to the appropriate manifest(s).  Here are some *examples*:
   <pre>makecatalogs</pre>
   * JRE and JDK for managed updates:
   <pre>manifestutil --add-pkg Oracle_Java_Plugin --section managed_updates --manifest some_manifest</pre>
   <pre>manifestutil --add-pkg Oracle_Java_JDK --section managed_updates --manifest some_manifest</pre>
   * JRE and JDK for offering in Managed Software Center:
   <pre>manifestutil --add-pkg Oracle_Java_Plugin --section optional_installs --manifest some_manifest</pre>
   <pre>manifestutil --add-pkg Oracle_Java_JDK --section optional_installs --manifest some_manifest</pre>

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
2. Python
   - http://www.pythonforbeginners.com/os/python-the-shutil-module
   - https://docs.python.org/2/library/shutil.html
3. Apple
   - https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/hdiutil.1.html
   - https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/pkgutil.1.html
   - https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/java_home.1.html
