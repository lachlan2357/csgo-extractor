#!/usr/bin/python3
import os
import getpass
import shutil

# check if run as root
if (getpass.getuser() != "root"):
    print("This program has to run with superuser privileges. Please run as root (or equivilent).")
    exit()

# initialisation
print(f"CSGO Exporter Installer")
homedir = f"/home/{os.environ.get('SUDO_USER', os.environ.get('USERNAME'))}"

# clone code
if ".csgo-extractor" in os.listdir(homedir):
    replace = input(f"  \u21B3 Existing download of CSGO Extractor found at {os.path.join(homedir, '.csgo-extractor')}. Do you want to replace it [y/N]? ")
    if (replace.lower() == "y"):
        pass
        #shutil.rmtree(os.path.expanduser(f"{homedir}/.csgo-extractor"))
    else:
        print("  \u21B3 Not replaceing install. Exiting.")
        exit()

#os.system(f"git clone -q https://github.com/lachlan2357/csgo-extractor {homedir}/.csgo-extractor")
os.system(f"chown -R {os.environ.get('SUDO_USER')}:{os.environ.get('SUDO_USER')} {homedir}/.csgo-extractor")

# check cloned code for required files
requiredfiles = ["csgo-extractor.py", "weaponfiletoitem.json"]
requiredfiles = []
for file in requiredfiles:
    if file not in os.listdir(f"{homedir}/.csgo-extractor"):
        print(f"  \u21B3 Warning: File {file} not found. Exiting.")
        exit()

# create symlink is /usr/bin/
print("  \u21B3 Creating symlink to file")
os.system(f"ln -sf {homedir}/.csgo-extractor/csgo-extractor.sh /usr/bin/csgo-extractor")

# make sure symlink is executable
print("  \u21B3 Giving symlink execution permissions")
os.system("chmod +x /usr/bin/csgo-extractor")