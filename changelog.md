# v0.2.0
## New
- Added import for all language files. While this information isn't extensively used, it will be further adopted in the future
- Added all other languages to the 'Place Names' entries
- Outputted data file now contains the version of the game exported to make it easier to keep track of different exports
- Added switch to change the directory used instead of always having to run the program from the correct directory

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