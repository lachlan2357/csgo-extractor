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