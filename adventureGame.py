import tkinter
from tkinter import StringVar, ttk
from tkinter.constants import OUTSIDE

#To do:
#Create room system (Very important!!)
# - Implement choice events into goTo instead of choices
# - Add battle roomType that can auto detect if its a normal or boss battle
# - In battle roomType all that has to be entered in content are the enemies and the min/max amount there is supposed to be of them
# - In boss roomType all that has to be entered in content is the boss and its dialogue
# - Add both ifWin and ifLose into battle and boss
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
# - Add possibility for shops
# - Add ability to make certain choices open up new dialogue options
# - Talking to npc should bring up 3 dialogue choices (based on highest in currentDialogue hierarchy) + shop when thats available
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
# - Create main menu when game is opened (has create new, load file and delete file on it)
#Support for multiple campaigns (which can all have multiple characters) (Very Important!!)
#Finish all player operated character functionalities
# - Implement checkHasItem in character class
# - Create dict with all thus far recruited members. Also make a list in which all names of members that are currently in the party reside
# - Create dict with players accomplishments (did quest, beat boss, ect)

mainWindow = tkinter.Tk()
mainWindow.configure(padx=50, pady=30)

class Characters: #Used for characters that have been recruited or are present within the team
    def __init__(self, characterData):
        self.__characterStats = {
            "name": characterData["name"],
            "health": characterData["health"],
            "maxHealth": characterData["maxHealth" if "maxHealth" in characterData.keys() else "health"],
            "attacks": characterData["attacks"] if "attacks" in characterData else {},
            "items": characterData["items"] if "items" in characterData else {}
        }

    def changeStat(self, changeHow, statToChange, value): #Can change any stat in this class (set value, add to, subtract from, append to list or dict or remove from list or dict)
        if statToChange in self.__characterStats:
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

    def checkStat(self, statToCheck): #Checks value of given stat
        if statToCheck in self.__characterStats:
            return self.__characterStats[statToCheck]
        else:
            raise ValueError(f"{statToCheck} is not an existing stat")

    def checkHasItem(self, item, notHas): #Should check if character has an item or not (not finished)
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

testRooms = { #This list is mostly used for me to visualize what creating rooms and such might look like
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
            },
            {
                "roomType": "battle",
                "content": {
                    "enemies": {"evil dave": 3, "even more evil dave": 1}
                }
            },
            {
                "roomType": "battle",
                "content": {
                    "boss": ["henk"],
                    "enemies": {"evil dave": 2},
                    "text": ["bla bla evil plot bla bla"]
                }
            }
        ]
    }
}

content = [[], []]

def theContentDestroyer9000(content, deleteAll=False): #Guess whos back. Back again. Not content thats for sure!
    for box in content[0]:
        box.destroy()
    content[0] = []
    if deleteAll:
        for box in content[1]:
            box.destroy()
        content[1] = []

def contentCreator(roomContent): #With the arival of lord contentDestroyer, only the brave contentCreator can end its reign of tyranny
    num = 0
    playerAnswer = StringVar()

    theContentDestroyer9000(content)

    for currentContent in roomContent:
        for currentText in currentContent[1]:
            if "blockIf" in currentText: #Checks if widget should be shown or not
                if checkIfHasAchievement(currentText["blockIf"]):
                    continue

            if currentContent[0] == "text": #Creates label
                currentWidget = tkinter.Label(text=currentText["data"])
            elif currentContent[0] == "choice": #Creates radio button       
                currentWidget = ttk.Radiobutton(
                    text=currentText["data"][0],
                    value=currentText["data"][1],
                    variable=playerAnswer
                )
            elif currentContent[0] == "button": #Creates button
                currentWidget = ttk.Button(
                    text=currentText["data"][0],
                    command=lambda toUse = currentText["data"][1] : funcExecute(toUse) #Turn this into a lambda function
                )
            else:
                raise ValueError(f"{currentContent[0]} is not a valid widget")
            
            if len(currentText["data"]) < 3:
                currentWidget.grid(column=0, row=num)
                num += 1
            else:
                currentWidget.place(bordermode=OUTSIDE, anchor="nw")
            content[0 if len(currentText["data"]) < 3 else 1].append(currentWidget)

def turnToNumber(value): #This is obsolete but im keeping it just to be sure
    try:
        value = float(value)
    except:
        return value
    finally:
        return value

def optionsMenu(): #Opens options menu
    pass

def talkTo(character): #Open dialogue menu (can also include shop)
    pass

def savePosition(): #Save in which area player resides
    pass

def checkIfHasAchievement(toCheck, needsAll=False): #Checks if the player has achieved certain conditions (with the exception of npc emotions)
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
            for character in toCheck["onTeam"]: #Checks if a given npc is on the players team
                if character in playerTeam or isinstance(character, array) and character[0] not in playerTeam:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break
        elif key == "defeatedBoss":
            for boss in toCheck["defeatedBoss"]: #Checks if the player has defeated a given boss
                if boss in playerAccomplishments["defeatedBosses"] or isinstance(boss, array) and boss[0] not in playerAccomplishments["defeatedBosses"]:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break


def funcExecute(functionToUse): #executes whatever function we put into it. useful for dynamically creating buttons
    if functionToUse in list(functionList.keys()):
        functionList[functionToUse]()

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

    def fullName(self): #Creates the full name of an npc
        return f"{self.firstName} {self.lastName}"

    @staticmethod
    def hierarchyCheck(dialogueList): #Checks what the highest hierarchy in a dialogue list is
        for tier, text in enumerate(dialogueList):
            if len(text) != 0:
                return tier
        raise ValueError("No dialogue found")

    def checkForNewDialogue(self): #Checks for new dialogue to put into currentDialogue (not finished yet)
        for hierarchyTier, values in enumerate(self.possibleDialogue):
            for dialogue in values[:]:
                passedCheck = False
                doBreak = False

                if "subText" in dialogue[0].keys():
                    pass
                else:
                    if "relation" in dialogue[0].keys(): #Checks emotion npc has for player
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

                    if "world" in dialogue[0].keys(): #Checks achievements player has accomplished
                        if checkIfHasAchievement(dialogue[0]["world"], needsAll=True):
                            passedCheck = True

                if passedCheck:
                    self.possibleDialogue[hierarchyTier].remove(dialogue)
                    self.addDialogue(hierarchyTier, dialogue)

    def addDialogue(self, tier, dialogue): #Adds dialogue to currentDialogue
        self.currentDialogue[tier].append([dialogue[1], dialogue[2]])

dialogue = { # concept dialogue list
    "currentDialogue":[
        [
            [["dslkgfsdlkgjslkg"], ["open up path(s)"]]
        ],
        [],
        [],
        [],
        []
    ],
    "possibleDialogue":[
        [
            [{"relation":{}, "world":{}}, ["dslkgfsdlkgjslkg"], ["open up path(s)"]]
        ],
        [],
        [],
        [],
        []
    ]
}

functionList = {
    "example": "insert function to execute here"
}

mainWindow.mainloop()