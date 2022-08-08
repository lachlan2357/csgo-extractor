import os
import sys
import re
import json
import datetime
import platform
import subprocess

# initialisation
files = {}
fileobjs = {}
data = {}
languages = []

# cstrike15 mode
cstrike15 = False
csgofolder = "csgo"
if ("csgo" not in os.listdir() and "cstrike15" in os.listdir()):
    cstrike15 = True
    csgofolder = "cstrike15"

# classes
class settings:
    version = "0.2.1"
    builddate = "05/08/2022"
    description = "CSGO Exporter reads game files to produce data about a specific build."
    helpcommands = {
        "-h, --help": "Display this help menu.",
        "-w, --warnings": "Displays warning messages. Can be useful for debugging.",
        "-s, --setup": "Displays steps to setup and use the tool.",
        "-d, --directory": "Specifies a CSGO install directory (uses current directory if flag not present).",
        "-q, --quiet": "Quiet Mode. Disables all console outputs, does not overwrite previous exports and does not open directory on completion."
    }
    warnings = False
    quiet = False
    pydir = os.path.dirname(os.path.abspath(__file__))

class terminalsettings:
    escape = "\033[0;"
    escapeend = "m"

    prefix = {
        "foreground": 3,
        "background": 4
    }

    suffix = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
        "reset": 9
    }

    styleprefix = {
        "reset": 0,
        "bright": 1,
        "dim": 2,
    }

class terminal:
    class color:
        def generate(mode:str, color:str):
            return f"{terminalsettings.escape}{terminalsettings.prefix[mode]}{terminalsettings.suffix[color]}{terminalsettings.escapeend}"

        black = generate("foreground", "black")
        red = generate("foreground", "red")
        green = generate("foreground", "green")
        yellow = generate("foreground", "yellow")
        blue = generate("foreground", "blue")
        magenta = generate("foreground", "magenta")
        cyan = generate("foreground", "cyan")
        white = generate("foreground", "white")
        reset = generate("foreground", "reset")

    class style:
        def generate(style:str):
            return f"{terminalsettings.escape}{terminalsettings.styleprefix[style]}{terminalsettings.escapeend}"

        reset = generate("reset")
        dim = generate("dim")
        bright = generate("bright")

class output:
    def start(name:str):
        if (settings.quiet):
            return
        print(f"- Extracting {name} info ...", end = None)
        return

    def done():
        if (settings.quiet):
            return
        output.donetask = True
        print("  \u21B3 Done.")

    def failed():
        if (settings.quiet):
            return
        print(f"{terminal.color.red}  \u21B3 Failed.{terminal.color.reset}")

    def check(name:str):
        if (settings.quiet):
            return
        print(f"- Checking {name} info ...")

    def process(name:str):
        if (settings.quiet):
            return
        print(f"- Processing {name} info ...")
    
    def regular(text:str):
        if (settings.quiet):
            return
        print(f"  \u21B3 {text}")
    
    def warn(warning:str, persistant:bool = False):
        if (settings.quiet):
            return
        if (settings.warnings or persistant):
            print(f"{terminal.color.yellow}  \u21B3 {warning}{terminal.color.reset}")
    
    def error(error:str, terminate:bool = False):
        if (settings.quiet):
            return
        print(f"{terminal.color.red}  \u21B3 {error}{terminal.color.reset}")
        if terminate:
            print("- Exiting ... ")
            exit()

    def skip(reason:str):
        if (settings.quiet):
            print(f"{terminal.style.dim}  \u21B3 Skipping: {reason}{terminal.style.reset}")

class csgofile:
    def removeleadingtabs(text:str):
        if (len(text) == 0):
            return text

        while (text[0] == "\t" or text[0] == " "):
            if len(text) == 1 and (text[0] in ["\t", " "]):
                text = ""
                break
            
            text = text[1:]

        return text

    def removeinbetweentabs(text:str):
        text = text.replace("\"", "-", 1)
        beginning = text.index("\"")
        text = text.replace("\"", "-", 1)
        end = text.index("\"")

        return [text[1:beginning], text[end + 1:-1]]

    def removetrailingtabs(text:str):
        while (text[-1] == "\t" or text[-1] == " "):
            text = text[:-1]

        return text

    def checkprereq(lst:list):
        for item in lst:
            if (not files[item]["exists"]):
                return False

        return True
    
    def convert(lines, recursion = 0):
        obj = {}
        noprocesslines = 0

        skiplines = 0
        for i in range(0, len(lines)):
            i += skiplines

            # break if we are at the end of the list - the for loop doesn't cover it since we are modifiying i each time
            if (i > len(lines) - 1):
                break

            line = lines[i]
            
            # option 1: blank line:
            if (len(line.replace("\t", "").replace(" ", "")) == 0):
                continue

            # option 1.5: if no blank lines, remove leading tabs
            line = csgofile.removeleadingtabs(line)

            # option 2: comments
            if (csgofile.removeleadingtabs(line)[0:2] == "//" or csgofile.removeleadingtabs(line)[0:2] == "# " or csgofile.removeleadingtabs(csgofile.removetrailingtabs(line)) == "#"):
                continue

            # option 3: variable
            if ([char for char in line].count("\"") >= 3 and re.search("[\t, ]*.*\".*\"[\t, ]*\".*", line)):
                # if the variable spans multiple lines
                if ([char for char in line].count("\"") % 2 != 0):
                    numquotes = 0
                    for index in range(0, len([char for char in line])):
                        character = [char for char in line][index]
                        if character == "\"" and [char for char in line][index - 1] != "\\":
                            numquotes += 1

                    if numquotes % 2 == 0:
                        break


                    # find where the variable ends
                    j = i + 1
                    while ([char for char in lines[j]].count("\"") % 2 == 0):
                        j += 1
                    
                    # addon missing lines
                    variableadder = ""
                    for _line in lines[i + 1:j + 1]:
                        variableadder += csgofile.removeleadingtabs(_line)
                    line += variableadder

                    # skip the next lines so not to get muddled up
                    skiplines += j - i
                
                lst = csgofile.removeinbetweentabs(csgofile.removetrailingtabs(line))
                counter = 0
                while (f"{lst[0]}[{counter}]" in obj.keys()):
                    counter += 1
                
                obj[f"{lst[0]}[{counter}]"] = lst[1]

                continue

            # option 3.1: variable with no quotes but has equals sign
            if (re.search("[a-zA-Z_]*[\t ]*=[\t ]*.*", line)):
                if ("//" in line and line.index("//") < line.index("=")):
                    break

                lst = line.split("=")

                counter = 0
                while (f"{lst[0]}[{counter}]" in obj.keys()):
                    counter += 1
                
                obj[f"{lst[0]}[{counter}]"] = lst[1]
                continue
            
            # option 4: beginning of a class
            if (re.search("^[\t, ]*\".*\"[\t, ]*$", line) and re.search("[\t ]*{[\t ]*", lines[lines.index(lines[i]) + 1])):
                j = i + 2
                bracketcount = 1
                while (bracketcount != 0):
                    if re.search("[\t, ]*{", lines[j]):
                        bracketcount += 1
                    
                    if re.search("[\t, ]*}", lines[j]):
                        bracketcount -= 1

                    j += 1
                
                _obj = csgofile.convert(lines[i + 1: j], recursion + 1)
                counter = 0
                line = csgofile.removetrailingtabs(line)
                keyprefix = line.replace("\"", "")
                key =  f"{keyprefix}[{counter}]"
                while key in obj.keys():
                    counter += 1
                    key =  f"{keyprefix}[{counter}]"

                obj[key] = _obj

                skiplines += j - i - 1
                continue           
            
            # option 5: just brackets
            if (re.search("^[\t ]*}[\t ]*$", line) or re.search("^[\t ]*{[\t ]*$", line)):
                continue
            
            # option 6: just values (only in navplace.db atm)
            if (re.search("^[a-zA-Z0-9]*$", line)):
                counter = 0
                while (f"[{counter}]" in obj.keys()):
                    counter += 1

                obj[f"[{counter}]"] = line
                continue
            
            # option 7: extension from 3 - variable with no quotes or equals sign but no dash
            if (re.search("^[\t ]*[a-zA-Z_0-9]+[\t ]+[a-zA-Z0-9/]+", line)):
                if (re.search("^[A-Za-z0-9 ]+\:$", line) and cstrike15):
                    continue
                
                if ("//" in line):
                    line = csgofile.removetrailingtabs(line[0:line.index("//")])
                
                lst = re.split("[\t ]", line)
                while "" in lst:
                    lst.remove("")

                for item in lst:
                    if item[0:2] == "//":
                        index = lst.index(item)
                        while len(lst) > index:
                            lst.pop()
                
                if len(lst) != 2:
                    output.error(f"Too many items to process. Skipping: {lst}")
                    continue
                
                counter = 0
                while (f"{lst[0]}[{counter}]" in obj.keys()):
                    counter += 1
                
                obj[f"{lst[0]}[{counter}]"] = lst[1]
                continue
            
            # option 8: separated by " - " instead with no quotes - seemingly only found in cstrike15_english.txt
            if (re.search("[A-Z1-9]+ +\- +[A-Za-z ]+", line) and cstrike15):
                lst = line.split(" - ")

                counter = 0
                while (f"{lst[0]}[{counter}]" in obj.keys()):
                    counter += 1
                
                obj[f"{lst[0]}[{counter}]"] = lst[1]
                continue

            # option 9: variable with quotes but the value is on the next lines - seemingly only found in cstrike15_english.txt
            if (re.search("^\"[A-Za-z]*\"[\t ]*$", line) and cstrike15):
                varline = lines[lines.index(lines[i]) + 1]
                if ([char for char in varline].count("\"") % 2 != 0):
                    # find where the variable ends
                    j = i + 2
                    while ([char for char in lines[j]].count("\"") % 2 == 0):
                        j += 1
                    
                    # addon missing lines
                    variableadder = ""
                    for _line in lines[i + 2:j + 1]:
                        variableadder += f"\n{csgofile.removeleadingtabs(_line)}"
                    varline += variableadder

                    # skip the next lines so not to get muddled up
                    skiplines += j - i + 1
                
                lst = [csgofile.removetrailingtabs(line), varline]
                counter = 0
                while (f"{lst[0]}[{counter}]" in obj.keys()):
                    counter += 1
                
                obj[f"{lst[0]}[{counter}]"] = lst[1]
                continue

            output.error(f"Line wasn't processed as it could not be categorised: {line}")
            noprocesslines += 1
        
        if (noprocesslines > 0):
            output.error(f"Could not process {noprocesslines}/{len(lines)} lines")

        if (len(obj.keys()) == 1 and recursion == 0):
            key = list(obj.keys())[0]
            if (key.split(".")[0].lower() in files.keys() or key[:-3].lower() in files.keys()):
                obj = obj[key]
        
        return obj

    def looper(key, workingprefab, corresponding, currentweaponobj, recursion = 0):
        if (len(corresponding) > 1 and type(corresponding) == "list"):
            print(corresponding)
            _key = corresponding[0]
            corresponding.pop(0)
            if (_key not in workingprefab.keys()):
                workingprefab[_key] = {}
            
            workingprefab[_key] = csgofile.looper(workingprefab[_key], corresponding, currentweaponobj, recursion + 1)
            return workingprefab

        if (corresponding[0] not in workingprefab.keys()):
            workingprefab[corresponding[0]] = currentweaponobj[key]
            return workingprefab
        else:
            return workingprefab

class extract:
    def build():
        output.start("build")
        prereq = csgofile.checkprereq(["steam"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        obj = {}

        dateindex = -1
        timeindex = -1
        months = ["Jan", "Feb", "Mar", "Apr", "May", 'Jun', 'Jul', "Aug", "Sep", "Oct", "Nov", 'Dec']

        for line in files["steam"]["split"]:
            info = line.split("=")
            donotadd = ["ProductName", "appID"]
            if (info[0] in donotadd or info[0] == ''): 
                continue

            if (info[0] == "VersionDate"):
                dateindex = files["steam"]["split"].index(line)
                if (dateindex >= 0 and timeindex >= 0):
                    obj["VersionDateTime"] = 0
                continue

            if (info[0] == "VersionTime"):
                timeindex = files["steam"]["split"].index(line)
                if (dateindex >= 0 and timeindex >= 0):
                    timelist = files["steam"]["split"][timeindex].split("=")[1].split(":")
                    datelist = files["steam"]["split"][dateindex].split("=")[1].split(" ")
                    date = datetime.datetime(int(datelist[2]), int(months.index(datelist[0])) + 1, int(datelist[1]), int(timelist[0]), int(timelist[1]), int(timelist[2]))
                    obj["VersionDateTime"] = (int(date.timestamp()))
                continue

            if (info[1].isdigit()):
                obj[info[0]] = int(info[1])
                continue
            
            obj[info[0]] = info[1]

        output.done()
        return obj

    def weapons():
        output.start("weapon")
        prereq = csgofile.checkprereq(["scripts", "csgo_english"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        allweapons = os.listdir(f"{files['scripts']['path']}")

        weaponsprefabobj = {}
        weaponsobj = {}
        discard = 0
        for file in allweapons:
            #only look for weapon files
            if (re.match("weapon\_.*\.txt", file) == None):
                discard += 1
                continue

            #specifically remove the 'template' weapon_rifle
            if (file == "weapon_rifle.txt"):
                discard += 1
                continue

            f = open(f"{files['scripts']['path']}/{file}", "r")
            content = f.read()
            lines = content.split("\n")

            obj = {}
            for line in lines:
                #remove lines that are just tabs and spaces or empty
                if (re.search("^[\t ]*$", line) != None or len(line) == 0):
                    continue

                #remove leading tabs and spaces
                #line += "-"
                while (line[0] == "\t" or line[0] == " "):
                    line = line[1:]

                #next line if comment or braces
                if (line[0:2] == "//" or line[0] == "{" or line[0] == "}"):
                    continue

                #remove comments on the end of the lines
                if ("//" in line):
                    line = line[:line.index("//")]

                #remove trailing tabs and spaces
                while (line[-1] == "\t" or line[-1] == " "):
                    line = line[0:-2]
                
                #next weapon if onto other data
                if (line in ["TextureData", "SoundData", "ModelBounds"]): 
                    break

                #remove quotes and replace tabs with '=' (have to do this bullshittery because of smoke grenade colours)
                openquote = False
                for char in line:
                    if (char == "\""):
                        openquote = not openquote
                        continue
                    if ((char == "\t" or char == " ") and openquote == False):
                        line = line.replace(char, "=", 1)
                line = line.replace("\"", "")

                #remove all but 1 '='
                line = line.replace("=", "", [char for char in line].count("=") - 1)

                add = line.split("=")

                #remove entries without values
                if (len(add) != 2):
                    continue

                if (add[1].isdigit()):
                    obj[add[0]] = int(add[1])
                    continue
                obj[add[0]] = add[1]

            #remove entries with no names
            if ("printname" not in obj.keys()):
                continue

            #remove non-csgo weapons
            if (re.search("SFUI_WPNHUD", obj["printname"]) == None):
                continue

            sfuilookup = obj["printname"][1:]
            match = re.search(f"\"{sfuilookup}\"(\t)*\".*\"", files["csgo_english"]["contents"])
            line = match.group()
            line = line.replace("\"", "", [char for char in line].count("\"") - 2)
            index = line.index("\"")
            weaponname = line[index + 1:-1]
            
            weaponsprefabobj[file[:-4]] = obj

        nofile = False
        errorreason = ""
        if ("items" not in os.listdir(f"{files['scripts']['path']}")):
            errorreason = "This version of CSGO does not have an items folder. Only using data provided in weapon files."
            nofile = True

        if (not nofile and "items_game.txt" not in os.listdir(f"{files['items']['path']}")):
            errorreason = "This version of CSGO does not have an item_game.txt file. Only using data provided in weapon files."
            nofile = True

        # load dictionary
        weapontransfer = json.loads(open(f"{settings.pydir}/weaponfiletoitem.json", "r").read())

        if (nofile and len(weaponsprefabobj) == 0):
            output.error("No weapon data can be retrieved from any known source.")
            output.failed()
            return {}
        
        if (nofile):
            output.warn(errorreason, True)
            weaponsobj = {}
            for weaponclass in weaponsprefabobj:
                currentweaponobj = weaponsprefabobj[weaponclass]
                obj = {}
                for key in currentweaponobj:
                    #remove team, it is always there and is stupid
                    if (key == "Team"):
                        continue

                    corresponding = weapontransfer[key].split("/")
                    workingprefab = json.loads(json.dumps(obj))

                    obj = csgofile.looper(key, workingprefab, corresponding, currentweaponobj)
            
                sfuilookup = obj["item_name"][1:]
                match = re.search(f"(?i)\"{sfuilookup}\"(\t)*\".*\"", files["csgo_english"]["contents"])
                line = match.group()
                line = line.replace("\"", "", [char for char in line].count("\"") - 2)
                index = line.index("\"")
                weaponname = line[index + 1:-1]

                weaponsobj[weaponname] = obj
            output.done()
            return weaponsobj

        itemsgame = open(files["items_game"]["path"]).read()
        allitems = re.findall("\"weapon_.*_prefab\"", itemsgame)

        #remove duplicates
        allitems = list(dict.fromkeys(allitems))

        for prefabname in allitems:
            match = re.search(prefabname + "\n(\t)*{", itemsgame)
            section = itemsgame[match.span()[1] + 1:]

            def txttoobj(section, recursion):
                openbrackets = 1
                length = 0
                while (openbrackets != 0):
                    if (section[length] == "{"):
                        openbrackets += 1
                    
                    if (section[length] == "}"):
                        openbrackets -= 1

                    length += 1
                section = section[:length - 1]

                obj = {}
                bracketcount = 0
                ignore = False
                for line in section.split("\n"):        
                    line += "-"
                    while line[0] == "\t":
                        line = line[1:]
                    
                    #remove empty lines
                    if (line == "-"):
                        continue
                    line = line [0:-1]

                    if (ignore):
                        if (line == "{"):
                            bracketcount += 1
                        
                        if (line == "}"):
                            bracketcount -= 1
                        
                        if (bracketcount == 0):
                            ignore = False
                        
                        continue

                    #three types of lines, obj keys, brackets, value pairs
                    #type 1: value pairs
                    if ([char for char in line].count("\"") == 4 and "\t" in line):
                        line = line.replace("\t", "", [char for char in line].count("\t") - 1)
                        line = line.split("\t")
                        
                        obj[line[0].replace("\"", "")] = line[1].replace("\"", "")
                        continue

                    #type 2: obj keys
                    if ("\t" not in line and line not in ["{", "}"] and [char for char in line].count("\"") == 2):
                        counter = 0
                        temp_section = section[section.index(line):]
                        while (temp_section[counter] != "{"):
                            counter += 1
                        
                        sendsection = temp_section[counter + 1:]
                        _obj = txttoobj(sendsection, recursion + 1)

                        obj[line.replace("\"", "")] = _obj
                        
                        continue

                    #type 3: brackets - ignore until closed
                    if (line == "{"):
                        ignore = True
                        bracketcount = 1
                        continue

                return obj

            obj = txttoobj(section, 0)

            if ("item_name" not in obj.keys()):
                _name = prefabname.replace("\"", "")
                output.warn(f"{_name} has no item_name attribute. Assuming it isn't a weapon available in game.")
                continue

            sfuilookup = obj["item_name"][1:]
            match = re.search(f"(?i)\"{sfuilookup}\"(\t)*\".*\"", files["csgo_english"]["contents"])
            line = match.group()
            line = line.replace("\"", "", [char for char in line].count("\"") - 2)
            index = line.index("\"")
            weaponname = line[index + 1:-1]

            if ("item_class" not in obj.keys()):
                output.warn(f"{weaponname} has no prefab specified. Only using what's provided in items_game.txt file.")
                weaponsobj[weaponname] = obj
                continue
                
            weaponclass = obj["item_class"]

            if (weaponclass not in weaponsprefabobj.keys()):
                output.warn(f"{weaponname}'s weapon file does not exist. Only using what's provided in items_game.txt file.")
                weaponsobj[weaponname] = obj
                continue

            currentweaponobj = weaponsprefabobj[weaponclass]
            for key in currentweaponobj:
                #remove team, it is always there and is stupid
                if (key == "Team"):
                    continue

                corresponding = weapontransfer[key].split("/")
                workingprefab = json.loads(json.dumps(obj))
                obj = csgofile.looper(key, workingprefab, corresponding, currentweaponobj)
            
            weaponsobj[weaponname] = obj

        output.done()
        return weaponsobj

    def weaponskins():
        output.start("weapon skin")
        prereq = csgofile.checkprereq(["items_game_cdn"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        obj = {}
        for line in files["items_game_cdn"]["split"]:
            if (len(line) == 0):
                continue

            if (line[0] == "#"):
                continue

            lst = line.split("=")
            obj[lst[0]] = lst[1]
        
        output.done()
        return obj

    def skincollections():
        output.start("skin collections")
        prereq = csgofile.checkprereq(["items_game"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        obj = {}
        master = fileobjs["items_game"]

        for key in master:
            if (re.search("^item_sets\[[0-9]*\]$", key)):
                currentset = master[key]
                for setkey in currentset:
                    set = currentset[setkey]
                    lookupname = f"{set['name[0]'][1:]}[0]"

                    # sometimes the caps don't line up for some reason. this is seemingly only in the gamma 2 case, so have to check for it
                    if (lookupname == "CSGO_set_gamma_2[0]"):
                        lookupname = "CSGO_set_Gamma_2[0]"

                    setname = fileobjs["csgo_english"]["lang[0]"]["Tokens[0]"][lookupname]
                    
                    if (setkey in obj.keys()):
                        output.warn("Key overwritten.")

                    obj[f"{setname}"] = set

        output.done()
        return obj
    
    def maps():
        output.start("map")
        prereq = csgofile.checkprereq(["maps"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        allmaps = os.listdir(files["maps"]["path"])

        mapsobj = {}
        for file in allmaps:
            if(re.search(".bsp", file) == None):
                continue
            
            with open(f"{files['maps']['path']}/{file}", encoding="iso_8859_1") as f:
                f.seek(1032)
                allbytes = f.read(4)
            read = bytes(allbytes, "iso_8859_1")
            revision = (int.from_bytes(read, 'little'))
            mapsobj[file[0:-4]] = revision

        output.done()
        return mapsobj

    def achievements():
        output.start("achievement")
        prereq = csgofile.checkprereq(["medalsconfig"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        obj = fileobjs["medalsconfig"]
        output.done()
        return obj

    def placenames():
        output.start("placename")
        prereq = csgofile.checkprereq(["navplace"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}
        
        names = []
        for place in files["navplace"]["split"]:
            if (place[0:2] == "//" or len(place) == 0):
                continue

            names.append(place)
        
        obj = {}

        for name in names:
            langobj = {}
            for lang in languages:
                key = f"csgo_{lang}"
                if f"{name}[0]" not in fileobjs[key]["lang[0]"]["Tokens[0]"].keys():
                    token = fileobjs["csgo_english"]["lang[0]"]["Tokens[0]"][f"{name}[0]"]
                else:
                    token = fileobjs[key]["lang[0]"]["Tokens[0]"][f"{name}[0]"]
                langobj[lang] = token
            obj[name] = langobj

        output.done()
        return obj

    def gamemodes():
        output.start("gamemode")
        prereq = csgofile.checkprereq(["gamemodes"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        #obj = csgofile.convert(files["gamemodes"]["split"], 0)
        obj = fileobjs["gamemodes"]
        output.done()
        return obj
    
    def gamemodesconfigs():
        output.start("gamemode configs")
        prereq = csgofile.checkprereq(["cfg"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        obj = {}
        dir = os.listdir(f"{files['cfg']['path']}")
        for filename in dir:
            if (not re.search("gamemode_.*\.cfg", filename)):
                continue
            
            lines = open(f"{files['cfg']['path']}/{filename}", "r").read().split("\n")
            _obj = {}
            for line in lines:
                if (line[0:2] == "//" or len(line) == 0):
                    continue

                if (re.search(".*[\t ]*.*\/\/", line)):
                    index = line.index("//")
                    line = line[0:index]

                if (re.match("^[\t ]*$", line)):
                    continue

                match = re.match("^([a-zA-Z\_])*", line)
                beginning = match.group()
                end = line[len(beginning):]
                while (end[0] == "\t" or end [0] == " "):
                    end = end[1:]

                end = csgofile.removetrailingtabs(end)

                _obj[beginning] = end
            obj[filename[9:-4]] = _obj

        output.done()
        return obj

    def defaultconfig():
        output.start("defaultconfig")
        prereq = csgofile.checkprereq(["config_default"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        lst = []
        for line in files["config_default"]["split"]:
            if (line[0:2] == "//" or len(line) == 0 or re.match("^[\t ]*$", line)):
                continue
            
            lst.append(csgofile.removetrailingtabs(line))
        output.done()
        return lst

    def musickits():
        output.start("music kit")
        prereq = csgofile.checkprereq(["items_game", "csgo_english"])
        if (not prereq):
            output.skip("File dependency missing.")
            return {}

        master = fileobjs["items_game"]
        obj = {}

        counter = -1
        while f"music_definitions[{counter + 1}]" in master.keys():
            counter += 1

        for definitionid in range(0, counter + 1):
            for kitid in master[f"music_definitions[{definitionid}]"]:
                if (kitid in obj.keys()):
                    output.error("Key overwritten.")
                
                kitcontents = master[f"music_definitions[{definitionid}]"][kitid]
                kitname = f'{kitcontents["loc_name[0]"][1:]}[0]'
                obj[kitname] = kitcontents

        output.done()
        return obj

# switches
skipper = 0
for i in range(1, len(sys.argv)):
    if i + skipper >= len(sys.argv):
        break
    
    argument = sys.argv[i + skipper]
    
    if (argument in ["-h", "--help"]):
        print(settings.description)
        print("\nCommands:")

        for command in settings.helpcommands:
            print(f"  {terminal.style.dim}{command}{terminal.style.reset} - {settings.helpcommands[command]}")

        exit()

    if (argument in ["-w", "--warnings"]):
        settings.warnings = True
        continue

    if (argument in ["-s", "--setup"]):
        terminaltype = {
            "Windows": "Open Command Prompt/PowerShell window here",
            "Linux": "Open in Terminal",
            "Darwin": "Open Directory in Terminal"
        }
        userterminal = terminaltype.get(platform.uname().system, "Open in Terminal")
        print(f"Setup Steps:\n1. Locate your CSGO Folder in your file manager.\n2. Right Click --> {userterminal}.\n3. Type the command 'python' followed by a space, but don't press enter. \n4. Locate this script in your file manager.\n5. Drag this file onto the terminal window. Execute the command.")
        exit()

    if (argument in ["-d", "--directory"]):
        index = i + 1

        try:
            newdir = sys.argv[index]
        except:
            output.error("No directory specified.", True)

        try:
            os.chdir(newdir)
        except:
            output.error("Directory could not be found", True)
    
        skipper += 1
        continue

    if (argument in ["-q", "--quiet"]):
        settings.quiet = True
        continue

    output.warn(f"Could not process argument {argument}. Use the --help argument for information about available arguments.", True)

if (not settings.quiet):
    print(f"CSGO Exporter v{settings.version}\nBuild Date {settings.builddate}\n")

# check directory to see if it is a csgo directory
output.check("directory")
if ("csgo" not in os.listdir() and "cstrike15" not in os.listdir()):
    output.error("This directory does not seem to contain a CSGO Install. Please find your CSGO Install directory and run this program from there.", True)

# static list of files
filelist = {
    "csgo/bspconvar_whitelist.txt": {
        "directory": False,
        "encoding": None
    },
    "csgo/cfg": {
        "directory": True
    },
    "csgo/gamemodes.txt": {
        "directory": False,
        "encoding": None,
    },
    "csgo/medalsconfig.txt": {
        "directory": False,
        "encoding": None,
    },
    "csgo/navplace.db": {
        "directory": False,
        "encoding": None
    },
    "csgo/steam.inf": {
        "directory": False,
        "encoding": None
    },
    "csgo/cfg/config_default.cfg": {
        "directory": False,
        "encoding": None
    },
    "csgo/maps": {
        "directory": True
    },
    "csgo/scripts": {
        "directory": True
    },
    "csgo/scripts/items": {
        "directory": True
    },
    "csgo/scripts/items/items_game.txt": {
        "directory": False,
        "encoding": None
    },
    "csgo/scripts/items/items_game_cdn.txt": {
        "directory": False,
        "encoding": None
    }
}

# process all language files
for fileprefix in os.listdir(os.path.join(csgofolder, "resource")):
    if (re.match("^(csgo|cstrike15)_\w*\.txt$", fileprefix)):
        languages.append(fileprefix[len(csgofolder) + 1:-4])
        filelist[f"csgo/resource/{fileprefix}"] = {
            "directory": False,
            "encoding": "utf16"
        }

for path in filelist:
    # check if file exists
    ogpath = path
    nameext = path.replace("/", "", [char for char in path].count("/") - 1)

    fileprefix = nameext[nameext.index("/") + 1:]
    if (not filelist[path]["directory"]):
        fileprefix = fileprefix[:fileprefix.index(".")]

    dirs = path.split("/")
    currentdir = os.getcwd()
    found = True
    for dir in dirs:
        if (dir not in os.listdir(currentdir)):
            if ("csgo" in dir and dir.replace("csgo", "cstrike15") in os.listdir(currentdir) and cstrike15):
                _dir = dir.replace("csgo", "cstrike15")
                currentdir += f"/{_dir}"
                continue
            if cstrike15:
                path = path.replace('csgo', 'cstrike15')
            output.warn(f"File {path} does not exist. Skipping all outputs that rely on it.", True)
            found = False
            break
        currentdir += f"/{dir}"

    if (not found):
        files[fileprefix] = {
            "exists": False
        }
        continue

    if (cstrike15):
        path = path.replace("csgo", "cstrike15")

    if (filelist[ogpath]["directory"]):
        files[fileprefix] = {
            "exists": True,
            "path": path
        }
        continue

    if (filelist[ogpath]["encoding"]):
        _file = open(path, "r", encoding=filelist[ogpath]["encoding"])
    else:
        _file = open(path, "r")

    _contents = _file.read()
    _split = _contents.split("\n")
    
    files[fileprefix] = {
        "exists": True,
        "path": path,
        "file": _file,
        "contents": _contents,
        "split": _split
    }
output.done()

# global file imports & processing
output.process("file")
for file in filelist:
    if (filelist[file]["directory"]):
        continue


    nameext = file.split("/")[-1]
    key = nameext[:nameext.index(".")]

    if (not files[key]["exists"]):
        output.skip(f"File '{nameext}' doesn't exist")
        continue

    output.regular(f"Processing {nameext} ...")
    fileobjs[key] = csgofile.convert(files[key]["split"])
output.done()

# extraction
data["Build"] = extract.build()
data["Weapons"] = extract.weapons()
data["WeaponSkinThumbnailLinks"] = extract.weaponskins()
data["WeaponSkinCollections"] = extract.skincollections()
data["Maps"] = extract.maps()
data["Achievements"] = extract.achievements()
data["PlaceNames"] = extract.placenames()
data["GameModes"] = extract.gamemodes()
data["GameModesConfigs"] = extract.gamemodesconfigs()
data["DefaultConfig"] = extract.defaultconfig()
data["MusicKits"] = extract.musickits()

# output
try:
    patchversion = data["Build"]["PatchVersion"]
except:
    patchversion = "unknown-version"

if (not settings.quiet):
    print("\n")

if ("output" not in os.listdir(settings.pydir)):
    os.mkdir(os.path.join(settings.pydir, "output"))

fileprefix = f"csgo-{patchversion.replace('.', '-')}"

if (f"{fileprefix}.json" in os.listdir(os.path.join(settings.pydir, "output"))):
    if (settings.quiet):
        overwrite = "n"
    else:
        overwrite = input("Data previously outputted, do you want to overwrite file? (y/N) ")

    if (overwrite.lower() != "y"):
        counter = 0
        while (f"{fileprefix}({counter}).json" in os.listdir(os.path.join(settings.pydir, "output"))):
            counter += 1
        fileprefix = f"{fileprefix}({counter})"

outputfile = open(f"{settings.pydir}/output/{fileprefix}.json", "w")
outputfile.write(json.dumps(data))
outputfile.close()

if (settings.quiet):
    exit()

fullpath = os.path.join(settings.pydir, "output", f"{fileprefix}.json")
print(f"Output file for CSGO Patch Version {patchversion} at {terminal.style.dim}{fullpath}{terminal.style.reset}")

# open directory dialog
input = input("Open Directory? (y/N): ")
if (input.lower() != "y"):
    exit()

if (platform.uname().system == "Windows"):
    os.startfile(os.path.join(settings.pydir, "output"))
else:
    if platform.uname().system == "Darwin":
        prefix = "open"
    else:
        prefix = "xdg-open"
    
    subprocess.call([prefix, os.path.join(settings.pydir, "output")])