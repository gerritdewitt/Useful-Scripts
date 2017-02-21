Munki “Nopkg” Automations
----------
The items in this directory all represent various automations and client configuration adjustments performed by Munki when systems check-in.

They are considered to be “nopkg” items because they don't actually install anything:  Instead, they perform their duties entirely via embedded script in the *pkginfo* metadata.

A common theme here is that each item will have two scripts:
   * An **installcheck** script, which measures the configuration state and determines if something should be done (“installed”).
      - Just as with an Apple pkg or dmg case, the *installcheck* script has the highest priority in determining if the item can be run or installed.
      - For example, we may use an installcheck script to check for the presence of a local user account that we remove periodically, measuring the time difference from now to when the account was created.
      - When the *installcheck* returns zero, this tells Munki that installation should proceed.  For nopkg items, this means that the *preinstall script* should run.  All other exit codes indicate to Munki that the “item is already  installed,” which, for nopkg items, means do not run the *preinstall* script.
   * A **preinstall** script.  Provided that the *installcheck* script returns zero, this script runs and makes the configuration adjustment.

Sources
----------
Some nopkg examples (see ReadMe.md files in each subfolder for relevant references):

1.  https://github.com/nmcspadden/PrinterGenerator
2.  http://scriptingosx.com/2014/12/control-ssh-access-with-munki-nopkg-scripts/
3.  https://jdmsysadmin.wordpress.com/2014/02/07/deployingrevoking-admin-rights-with-munki/
