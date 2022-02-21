import tkinter
from tkinter import StringVar, ttk

#To do:
#Create room system (Very important!!)
# - Implement choice events into goTo instead of choices
#Create battle system (the line layer system) (Important)
# - Npc attacks are controlled by the player
# - If an entity stands on a higher line. Those on lines behind it cannot be attacked but can still attacked
# - Npcs and the player can be moved from line to line during their turn
# - Npcs and player attacks can be removed and added
# - Attacks can be learned by either leveling up or buying them from a shop
# - Every character has mana. Some attacks take mana and others dont. If mana reaches 0 the mana attacks cannot be used anymore
#Create npc dialogue system (Important)
# - Npcs should be able to get recruited based on certain criteria
# - Npcs recruited can be put inside or removed from the team
# - Implement functionality for passedCheck within checkForNewDialogue (should activate addDialogue)
# - Implement addDialogue to add dialogue to currentDialogue dict
# - Add possibility for shops
#Create inventory system (Normal importance)
# - Items can be equipped from here
#Create item support for characters (Normal importance)
# - Items can give special bonusses like +atk, +def or +agility but can also give special bonusses like extra attack done to wolf enemies
# - Items maybe can have a kind of debuff attached to them like -2 def or extra damage taken from wolf enemies
#Create loot system (for things like gold for shops and items that can be picked up) (Lesser importance)
# - Bosses might be able to drop special items that can only be obtained from them
# - Gold obtained from killing enemies should be a mix between random and set
#Create options menu with current zone, health, cheatcodes, ect (Parity)
#Support for multiple save files (Very imporant!!)
# - Reminder that obj.__dict__ is a thing
#Support for multiple campaigns (which can all have multiple characters) (Very Important!!)
#Finish all player operated character functionalities
# - Implement checkHasItem in character class
# - Create dict with all thus far recruited members. Also make a list in which all names of members that are currently in the party reside
# - Create dict with players accomplishments (did quest, beat boss, ect)

mainWindow = tkinter.Tk()
mainWindow.configure(padx=50, pady=30)

class Characters:
    def __init__(self, characterData):
        self.__characterStats = {
            "name": characterData["name"],
            "health": characterData["health"],
            "maxHealth": characterData["maxHealth" if "maxHealth" in characterData.keys() else "health"],
            "attacks": characterData["attacks"] if "attacks" in characterData else {},
            "items": characterData["items"] if "items" in characterData else {}
        }

    def changeStat(self, changeHow, statToChange, value):
        if statToChange in __characterStats:
            if changeHow == "set":
                self.__characterStats[statToChange] = value
            elif changeHow == "add":
                self.__characterStats[statToChange] += value
            elif changeHow == "subtract":
                self.__characterStats[statToChange] -= value
            elif changeHow == "append":
                self.__characterStats[statToChange].append(value)
            elif changeHow == "remove":
                self.__characterStats[statToChange].remove(value)
            else:
                raise ValueError(f"{changeHow} is not a valid way to change stat")
        else:
            raise ValueError(f"{statToChange} is not an existing stat")

    def checkStat(self, statToCheck):
        if statToCheck in self.__characterStats:
            return self.__characterStats[statToCheck]
        else:
            raise ValueError(f"{statToCheck} is not an existing stat")

    def checkHasItem(self, item, notHas):
        pass

playableCharacters = {
    "campaign": {
        "hero": {
            "health": 10,
            "attacks": {
                "blazing sun": 25
            }
        }
    }
}

testRooms = {
    "campaign": {
        "forest":[
            {
                "roomType": "normal",
                "content": [
                    ["choice", [{"data": ["Talk to dave", "dave"],
                        "blockIf": {
                            "hasItem": ["big knife", ["truly humongous knife"]],
                            "OnTeam": [["dave"]],
                            "defeatedBoss": ["john", ["big man the almighty"]]
                        }}]]],
                "choiceEvent": {
                    "dave": ["talkTo", "dave"],
                    "exit": ["goTo", "forest", 5]
                }
            }
        ]
    }
}

content = [[], []]

def theContentDestroyer9000(content, deleteAll=False): #guess whos back. back again. not content thats for sure!
    for box in content[0]:
        box.destroy()
    content[0] = []
    if deleteAll:
        for box in content[1]:
            box.destroy()
        content[1] = []

def contentCreator(roomContent):
    num = [0, 0]
    playerAnswer = StringVar()

    theContentDestroyer9000(content)

    for currentContent in roomContent:
        for currentText in currentContent[1]:
            if currentContent[0] == "text":
                currentWidget = tkinter.Label(text=currentText)
            elif currentContent[0] == "choice":
                if "blockIf" in currentText:
                    if checkIfHasAchievement(currentText["blockIf"]):
                        continue
                
                currentWidget = ttk.Radiobutton(
                    text=currentText["data"][0],
                    value=currentText["data"][1],
                    variable=playerAnswer
                )
            elif currentContent[0] == "button":
                currentWidget = ttk.Button(
                    text=currentText[0],
                    command=currentText[1]
                )
            else:
                raise ValueError(f"{currentContent[0]} is not a valid widget")
            
            currentWidget.grid(column=0, row=num[0])
            content[0].append(currentWidget)
            num[0] += 1

def turnToNumber(value):
    try:
        value = float(value)
    except:
        return value
    finally:
        return value

def optionsMenu():
    pass

def talkTo(character):
    pass

def savePosition(): #Save in which area player resides
    pass

def checkIfHasAchievement(toCheck, needsAll=False):
    hasAll = True
    for key in toCheck:
        if key == "hasItem":
            for item in toCheck["hasItem"]: #This should loop through all characters within the team
                if checkHasItem(item[0] if isinstance(item, array) else item, "not" if isinstance(item, array) else "has"):
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break
        elif key == "onTeam":
            for character in toCheck["onTeam"]:
                if character in playerTeam or isinstance(character, array) and character[0] not in playerTeam:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break
        elif key == "defeatedBoss":
            for boss in toCheck["defeatedBoss"]:
                if boss in playerAccomplishments["defeatedBosses"] or isinstance(boss, array) and boss[0] not in playerAccomplishments["defeatedBosses"]:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break


#--------------------------------------------------------------------------------Dialogue system stuff

class npc:
    def __init__(self, characterInfo, currentDialogue, possibleDialogue, recruitStats=None):
        self.firstName = characterInfo[0]
        self.lastName = characterInfo[1]
        self.dialogue = dialogue
        self.emotions = {
            "anger": 0,
            "happiness": 0,
            "sadness": 0
        }
        self.recruitStats = recruitStats

    def fullName(self):
        return f"{self.firstName} {self.lastName}"

    def hierarchyCheck(self):
        for key, text in self.currentDialogue.items():
            if len(text) != 0:
                return key
        raise ValueError("No dialogue found")

    def checkForNewDialogue(self):
        for hierarchyTier in self.possibleDialogue:
            for dialogue in hierarchyTier:
                passedCheck = False
                doBreak = False

                if "subText" in dialogue[0].keys():
                    pass
                else:
                    if "relation" in dialogue[0].keys():
                        for emotion, value in dialogue[0]["relations"].items():
                            if emotion in self.emotions.keys():
                                if value >= self.emotions[emotion]:
                                    passedCheck = True
                                else:
                                    passedCheck = False
                                    doBreak = True
                                    break
                            else:
                                raise ValueError(f"{emotion} not in emotions")

                    if doBreak:
                        continue

                    if "world" in dialogue[0].keys():
                        if checkIfHasAchievement(dialogue[0]["world"], needsAll=True):
                            passedCheck = True

                if passedCheck:
                    pass

dialogue = { # concept dialogue list
    "currentDialogue":{
        1: [
            [["dslkgfsdlkgjslkg"], ["open up path(s)"]]
        ],
        2: [],
        3: [],
        4: [],
        5: []
    },
    "possibleDialogue":{
        1: [
            [{"relation":{}, "world":{}}, ["dslkgfsdlkgjslkg"], ["open up path(s)"]]
        ],
        2: [],
        3: [],
        4: [],
        5: []
    }
}

mainWindow.mainloop()