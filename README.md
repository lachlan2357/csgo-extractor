# CSGO Extractor
A simple command-line tool for extracting data from a CSGO Installation.

**Note this is still in pre-release. There will be bugs and not all features are present or fully completed. Everything is subject to change.**

## Features
As of version 0.1, the script can currently extract:
- some build information
- weapon data
- urls linking to weapon skin thumbnails
- weapon collections
- map names & their version
- list of achievements
- nav locations
- list of game-modes
- game mode configs
- default player config
- list of music kits

## Dependencies
The only dependency required is an install of Python3. If you wish to use the Linux installer script, you will also need git installed.

## Download & Running
There are currently two ways to use the tool.

### Universal Download | Any Platform
1. Download the source code by cloning the repository
2. Find the directory of your CSGO install and open a command-line window there.
3. Type the ```python``` command followed by a space, then drag the ```extractor.py``` file onto the command-line window to paste it's directory.
4. Execute that command.

### Installer File | Linux
1. Download the specific ```install.sh``` file from [here](https://raw.githubusercontent.com/lachlan2357/csgo-extractor/main/install.sh) or by running ```$ wget https://raw.githubusercontent.com/lachlan2357/csgo-extractor/main/install.sh```.
2. Ensure the file has permission to execute, changed through right clicking on it in your file manager and heading to the permissions tab, or by running ```$ sudo chmod +x install.sh``` in the directory.
3. Run the script.
4. If no errors occurred, you should have a ```csgo-extractor``` command. available. Ensure you use this command inside your CSGO install directory. 
