# v0.3.0
## New
- Added --version argument to only output the current program version. Can be useful if embedding into other programs
- Added an update checker to the beginning of the script to warn if the current version is outdated
- Replaced the terminal colouring with Colour Splash: my new python module to easily handle terminal colouring
- Added a check if the required colour_splash and requests modules are installed.
- Added the option to install missing required modules. Program will exit if they aren't installed
- Added switch to enable terminal colouring on Windows. By default this is disabled as it causes issues if you are using a default shell such as PowerShell or CMD
- Files now include a .bat file for Windows users to use as a frontend instead

## Fixed
- Updated README to feature recent additions and streamline syntax
- Reordered switches so they execute in a more preferable sequence, providing a more consistent experience
- Fixed issue where some lines in CSGO language files weren't processed due to an error with detecting where multi-line values start and finish
- Changed the line endings of both .sh files to Unix as this could have caused issues

## Notes
- As of this version, the program requires both the `requests` and `colour_splash` modules to be installed

# v0.2.1
## New
- Warnings are thrown if an unrecognised argument is parsed to the program no matter if warnings are enabled
- Added exception to the patch version appended to the end of the outputted file. If the patch version could not be determined, the file will be called "csgo-unknown-version.json"

## Fixed
- Removed the unintended space between the two dashes and the 'quiet' text in the help menu's entry for quiet mode
- Stopped outputting program name, version and build date when quiet mode was switched on
- Stopped outputting each start when quiet mode was switched on
- Removed the output when processing new directory as it interfered with other aspects of the program
- Added missing mention of quiet mode to v0.2's changelog
- Fixed issue with misbehaving check to determine whether a variable's value spanned multiple lines

## Known Issues
- Some lines in CSGO language files aren't processed due to the program not being able to recognise patterns in them. This will have to be resolved on a case-by-case-basis

# v0.2.0
## New
- Added import for all language files. While this information isn't extensively used, it will be further adopted in the future
- Added all other languages to the 'Place Names' entries
- Outputted data file now contains the version of the game exported to make it easier to keep track of different exports
- Added switch to change the directory used instead of always having to run the program from the correct directory
- Added switch to turn on quiet mode, where no outputs to the console will occur

## Fixed
- Fixed issue when processing lines from files where attempting to remove unnecessary characters resulted in an error

## Known Issues
- Some lines in CSGO language files aren't processed due to the program not being able to recognise patterns in them. This will have to be resolved on a case-by-case-basis

# v0.1.1
## New
- Added terminal check to directory so the program won't run if the directory doesn't contain a csgo or cstrike15 folder
- Added an option to choose whether to overwrite previously-extracted data after extraction process

## Fixed
- Removed debug output of each skin collection name
- Added missing entry for 'setup' under the help menu
- csgo-extractor.sh is executable by default, so making it so shouldn't be required

# v0.1.0
Initial Release