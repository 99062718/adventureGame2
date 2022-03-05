import tkinter
import random
from tkinter import StringVar, ttk, messagebox
from tkinter.constants import OUTSIDE

#To do:
#Create room system (Very important!!)
# - Add battle roomType that can auto detect if its a normal or boss battle
# - In battle roomType all that has to be entered in content are the enemies and the min/max amount there is supposed to be of them
# - Add both ifWin and ifLose into battle
# - Add extra settings that count for the entire campaign (such as party size limits)
#Create battle system (the line layer system) (Important)
# - Npc attacks are controlled by the player
# - If an entity stands on a higher line. Those on lines behind it cannot be attacked but can still attacked
# - Npcs and the player can be moved from line to line during their turn
# - Npcs and player attacks can be removed and added
# - Attacks can be learned by either leveling up or buying them from a shop
# - Every character has mana. Some attacks take mana and others dont. If mana reaches 0 the mana attacks cannot be used anymore
# - Add check to see if battle already exists within currentRegionExtra
#Create npc dialogue system (Important)
# - Npcs should be able to get recruited based on certain criteria
# - Add possibility for shops
# - Add ability to make certain choices open up new dialogue options
# - Talking to npc should bring up 3 dialogue choices (based on highest in currentDialogue hierarchy) + shop when thats available
#Create inventory system (Normal importance)
# - Items can be equipped from here
# - Implement shared inventory instead of personal inventories
#Create item support for characters (Normal importance)
# - Items can give special bonusses like +atk, +def or +agility
#Create loot system (for things like gold for shops and items that can be picked up) (Lesser importance)
# - Gold and xp obtained from killing enemies should be a mix between random and set
#Create settings menu with current zone, health, cheatcodes, ect (Parity)
# - Add ability to change line position per team member outside battle
#Support for multiple save files (Very imporant!!)
# - Reminder that obj.__dict__ is a thing
# - Battles are going to be a bit of a hard one. Save all enemies to currentRegionExtra and save that to json

#Ideas to flesh the game out a bit more:
#Items
# - Life steal
# - Durability (dont have to be used for every item)
# - Consumables
# - Extra loot dropped (higher chance at enemy dropping their items or more gold)
# - Thing that happen depending on the percentage of health the player has (more attack, higher crit chance, more defense, ect)
# - Events that trigger when crit happens (Gain health when crit, gain money on crit, ect)
# - Items that are better against certain types of monsters
#Battle
# - A template system so that frequently used enemy combos dont have to constantly be written out in its entirety
#Bosses
# - Bosses might be able to drop special items that can only be obtained from them
#Rooms
# - Dungeons (this is to fix balancing for battles and xp is extremely difficult as is)

mainWindow = tkinter.Tk()
mainWindow.configure(padx=50, pady=30)

#--------------------------------------------------------------------------------Dictionaries

customItems = {
    "Henk's dagger": {
        "speed": 2,
        "attackMulti": 0.25,
        "lifeDrain": ["wither"],
        "bodyParts": ["left", "right"]
    },
    "truly humongous knife": {
        "speed": 5,
        "lifeSteal": 20,
        "lifeDrain": ["fire", "poison"],
        "bodyParts": ["left", "right"]
    }
}

playableCharacters = {
    "campaign": {
        "hero": {
            "name": "hero the 4th",
            "health": 10,
            "mana": 0,
            "attacks": {
                "blazing sun": 25
            },
            "equippedItems":{
                "left": "truly humongous knife"
            }
        }
    }
}

customEnemies = {
    "evil dave": {
        "name": "evil dave",
        "health": 10,
        "mana": 0,
        "attacks": {
            "blazing sun": 25
        },
        "equippedItems":{
            "left": "truly humongous knife"
        }
    },
    "even more evil dave": {
        "name": "even more evil dave",
        "health": 25,
        "mana": 200,
        "speed": 5,
        "attacks": {
            "blazing sun": 25
        },
        "equippedItems":{
            "left": "truly humongous knife"
        }
    }
}

campaigns = { #This list is mostly used for me to visualize what creating rooms and such might look like
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
                        }},{"data": ["go to base", "base"]},{"data": ["exit", "exit"]}]],
                        ["button", [{"data": ["Choose", "nextRoom"]}]]],
                "choiceEvents": {
                    "dave": ["talkTo", "dave"],
                    "exit": ["goTo", "forest", 1],
                    "base": ["base"]
                }
            },
            {
                "roomType": "battle",
                "content": {
                    "enemies": {"evil dave": {"timesAppear": [1, 5], "onLine": 2}, "even more evil dave": {"timesAppear": 1}}
                },
                "choiceEvents": {
                    "ifWin": ["goTo", "forest", 0]
                }
            },
            {
                "roomType": "battle",
                "content": {
                    "boss": ["henk"],
                    "enemies": {"evil dave": {"timesAppear": 2}},
                    "text": ["bla bla evil plot bla bla"]
                }
            }
        ]
    },
    "2": 0
}

characterDict = {}
playerAccomplishments = { #Add all player accomplishments (like beating a boss) to this
    "defeatedBosses": []
}
currentRegionExtra = {} #This is for keeping track of the player being in battle, base, or talking to an npc
content = [[], []]

#--------------------------------------------------------------------------------Characters and enemies

class person: #Creates class from which characters and enemies inherit

    def __init__(self, characterData):
        self._characterStats = {
            "name": characterData["name"],
            "health": characterData["health"],
            "maxHealth": characterData["maxHealth" if "maxHealth" in characterData.keys() else "health"],
            "attacks": characterData["attacks"] if "attacks" in characterData.keys() else {},
            "attackMulti": characterData["attackMulti"] if "attackMulti" in characterData.keys() else 1,
            "speed": characterData["speed"] if "speed" in characterData.keys() else 1,
            "defense": characterData["defense"] if "defense" in characterData.keys() else 1,
            "mana": characterData["mana"],
            "maxMana": characterData["maxMana"] if "maxMana" in characterData.keys() else characterData["mana"],
            "onLine": characterData["onLine"] if "onLine" in characterData.keys() else 0,
            "equippedItems": {
                "left": characterData["equippedItems"]["left"] if "left" in characterData["equippedItems"].keys() else None,
                "right": characterData["equippedItems"]["right"] if "right" in characterData["equippedItems"].keys() else None,
                "head": characterData["equippedItems"]["head"] if "head" in characterData["equippedItems"].keys() else None,
                "chest": characterData["equippedItems"]["chest"] if "chest" in characterData["equippedItems"].keys() else None,
                "legs": characterData["equippedItems"]["legs"] if "legs" in characterData["equippedItems"].keys() else None,
                "feet": characterData["equippedItems"]["feet"] if "feet" in characterData["equippedItems"].keys() else None,
                "amulet": characterData["equippedItems"]["amulet"] if "amulet" in characterData["equippedItems"].keys() else None
            },
            "lifeSteal": characterData["lifeSteal"] if "lifeSteal" in characterData.keys() else 0,
            "lifeDrain": characterData["lifeDrain"] if "lifeDrain" in characterData.keys() else []
        }

        for bodyPart, item in self._characterStats["equippedItems"].items():
            if item:
                self.changeItemModifyer(item)

        self.setItem("left", "Henk's dagger")


    def changeStat(self, changeHow, statToChange, value): #Can change any stat in this class (set value, add to, subtract from, append to list or dict or remove from list or dict)
        if statToChange in self._characterStats:
            if changeHow == "set":
                self._characterStats[statToChange] = value
            elif changeHow == "add":
                self._characterStats[statToChange] += value
            elif changeHow == "subtract":
                self._characterStats[statToChange] -= value
            elif changeHow == "append":
                if isinstance(value, dict):
                    self._characterStats[statToChange][list(value.keys())[0]] = value
                else:
                    self._characterStats[statToChange].append(value)
            elif changeHow == "remove":
                self._characterStats[statToChange].remove(value)
            else:
                raise ValueError(f"{changeHow} is not a valid way to change stat")
        else:
            raise ValueError(f"{statToChange} is not an existing stat")

    def checkStat(self, statToCheck): #Checks value of given stat
        if statToCheck in self._characterStats:
            return self._characterStats[statToCheck]
        else:
            raise ValueError(f"{statToCheck} is not an existing stat")

    def setItem(self, bodyPart, item): #Sets item of given bodypart
        pastItem = self.checkItem(bodyPart)
        if pastItem:
            print(pastItem)
            self.changeItemModifyer(pastItem, True)
        self._characterStats["equippedItems"][bodyPart] = item
        self.changeItemModifyer(item)

    def checkItem(self, bodyPart):
        return self._characterStats["equippedItems"][bodyPart]

    def changeItemModifyer(self, item, remove=False): #Adds or removes item modifyer from person stats
        toChange = None

        for modifier, value in customItems[item].items():
            match modifier: #Gives an error in my IDE. Works perfectly though...
                case ("maxHealth" | "attackMulti" | "speed" | "maxMana" | "lifeSteal" | "defense"):
                    self.changeStat("subtract" if remove else "add", modifier, value)
                case "lifeDrain":
                    for lifeDrainModifier in value:
                        self.changeStat("remove" if remove else "append", "lifeDrain", lifeDrainModifier)

    @classmethod
    def changeTeam(cls, obj, addOrRemove="add"): #Adds/removes person to/from class onTeam
        if obj:
            if addOrRemove == "add":
                cls.onTeam.append(obj)
            else:
                cls.onTeam.remove(obj)
            return True
        else:
            return False

#-------------------------------------------------Characters

class characters(person): #Used for characters that have been recruited or are present within the team
    onTeam = []

    def __init__(self, characterData):
        super().__init__(characterData)
        self._characterStats["inventory"] = characterData["inventory"] if "inventory" in characterData else []
        for bodyPart, value in self._characterStats["equippedItems"].items(): #Adds all currently equipped items to inventory
            if value:
                self._characterStats["inventory"].append(value)

    def checkHasItem(self, item, notHas): #Should check if character has an item or not (not finished)
        inInventory = self.checkStat("inventory")
        if item in inInventory and notHas == "has" or item not in inInventory and notHas == "not":
            return True
        return False

def addToCharacterDict(toAdd): #Adds newly recruited people to character class and characterDict
    global characterDict
    characterDict[toAdd["name"]] = characters(toAdd)
    characters.changeTeam(toAdd["name"])

#-------------------------------------------------Character base

def goToBase(): #Goes to player base where team members can be swapped out
    global currentRegionExtra
    currentRegionExtra["base"] = "ayo"

    contentCreator([
        ["text", [{"data": ["Welcome to the base!"]}]],
        ["button",[
            {"data": ["Add to team", "addToTeamMenu"]},
            {"data": ["Remove from team", "removeFromTeamMenu"]},
            {"data": ["Exit base", "backToCampaign"]}
        ]]
    ])

def addToTeamMenu(): #Player can choose what character they want to add to their team
    if len(characters.onTeam) < len(characterDict):
        contentCreator([
            ["text", [{"data": ["Which character would you like to add to your party?"]}]],
            ["choice", [{"data": [x, x], "blockIf": {"onTeam": [x]}} for character in characterDict]],
            ["button", [{"data": ["Choose character", "addToTeam"]}, {"data": ["Back", "goToBase"]}]]
        ])
    else:
        messagebox.showerror(message="There are currently no characters available to put in your team!")

def addToTeam(): #Adds character to team and returns to base if succesful
     ifSuccesful = characters.changeTeam(playerAnswer.get())
     if ifSuccesful:
         goToBase()

def removeFromTeamMenu(): #Player can choose what character they want to remove from their team
    if len(characters.onTeam) != 1:
        contentCreator([
            ["text", [{"data": ["Which character would you like to remove from your party?"]}]],
            ["choice", [{"data": [x, x]} for character in characters.onTeam]],
            ["button", [{"data": ["Choose character", "removeFromTeam"]}, {"data": ["Back", "goToBase"]}]]
        ])
    else:
        messagebox.showerror(message="Characters cannot be removed while team size is 1!")

def removeFromTeam(): #Removes character from team and returns to base if succesful
     ifSuccesful = characters.changeTeam(playerAnswer.get(), "remove")
     if ifSuccesful:
         goToBase()

#-------------------------------------------------Enemies

class enemies(person): #Used for enemies currently in battle with
    onTeam = []

    def __init__(self, characterData):
        super().__init__(characterData)

#--------------------------------------------------------------------------------Room generation

def roomTypeCheck(currentRoom): #Checks roomType of room
    if currentRoom["roomType"] == "normal":
        contentCreator(currentRoom["content"], currentRoom["choiceEvents"])
    elif currentRoom["roomType"] == "battle":
        battleInnitializer(currentRoom["content"], currentRoom["choiceEvents"])
    else:
        raise ValueError(f"{currentRoom['roomType']} is not a valid roomType")

def nextRoom(data): #Goes to next room
    global currentRegion
    if playerAnswer.get() in data.keys():
        if data[playerAnswer.get()][0] == "goTo": #Goes to given room (should also use saveData function)
            currentRegion = [data[playerAnswer.get()][1], data[playerAnswer.get()][2]]
            roomTypeCheck(campaigns[currentCampaign][currentRegion[0]][currentRegion[1]])
        elif data[playerAnswer.get()][0] == "talkTo": #Goes into dialogue menu with npc
            talkTo(playerAnswer.get())
        elif data[playerAnswer.get()][0] == "base": #Goes to player base
            goToBase()
    else:
        print(playerAnswer.get(), data)
        messagebox.showerror(message="Please select one of the choices")

def theContentDestroyer9000(content, deleteAll=False): #Guess whos back. Back again. Not content thats for sure!
    for box in content[0]:
        box.destroy()
    content[0] = []
    if deleteAll:
        for box in content[1]:
            box.destroy()
        content[1] = []

def contentCreator(roomContent, extraData=None): #With the arival of lord contentDestroyer, only the brave contentCreator can end its reign of tyranny
    global playerAnswer
    num = 0
    playerAnswer = StringVar()

    theContentDestroyer9000(content)

    for currentContent in roomContent:
        for currentText in currentContent[1]:
            if "blockIf" in currentText: #Checks if widget should be shown or not
                if checkIfHasAchievement(currentText["blockIf"]):
                    continue

            if currentContent[0] == "text": #Creates label
                currentWidget = tkinter.Label(text=currentText["data"][0])
            elif currentContent[0] == "choice": #Creates radio button       
                currentWidget = ttk.Radiobutton(
                    text=currentText["data"][0],
                    value=currentText["data"][1],
                    variable=playerAnswer
                )
            elif currentContent[0] == "button": #Creates button
                currentWidget = ttk.Button(
                    text=currentText["data"][0],
                    command=lambda toUse=currentText["data"][1], extraData=extraData if extraData else None: funcExecute(toUse, extraData) if extraData else funcExecute(toUse) #Turn this into a lambda function
                )
            else:
                raise ValueError(f"{currentContent[0]} is not a valid widget")
            
            if len(currentText["data"]) < 3:
                currentWidget.grid(column=0, row=num)
                num += 1
            else:
                currentWidget.place(bordermode=OUTSIDE, anchor="nw")
            content[0 if len(currentText["data"]) < 3 else 1].append(currentWidget)

def backToCampaign(): #Goes back to where campaign left off
    global currentRegionExtra
    currentRegionExtra = {}
    theContentDestroyer9000(content, deleteAll=True)
    contentCreator([["button", [{"data": ["Settings", "openSettingsMenu", ""]}]]])
    roomTypeCheck(campaigns[currentCampaign][currentRegion[0]][currentRegion[1]])

#--------------------------------------------------------------------------------Battle

{ #Just here for me to remember what i need to implement into battle
                "roomType": "battle",
                "content": {
                    "boss": ["henk"],
                    "enemies": {"evil dave": {"timesAppear": 2}},
                    "text": ["bla bla evil plot bla bla"]
                }
            }

# { list to visualize how i want to store save data during battle
#   "currentEnemies": [insert list here],
#   "turns": [insert list of when characters can attack and whos turn it is]
# }

def battleInnitializer(roomContent, choiceEvents): #Innitiates battle
    usedEnemiesDict = {}
    for enemyName, enemyData in roomContent["enemies"].items():
        timesAppear = 1 if "timesAppear" not in enemyData else enemyData["timesAppear"] if not isinstance(enemyData["timesAppear"], list) else random.randint(enemyData["timesAppear"][0], enemyData["timesAppear"][1])
        if timesAppear == 1:
            usedEnemiesDict[enemyName] = createEnemy(enemyName, enemyData)
            enemies.changeTeam(enemyName)
        else:
            for timesAppeared in range(timesAppear):
                newName = f"{enemyName}{timesAppeared + 1}"
                usedEnemiesDict[newName] = createEnemy(enemyName, enemyData)
                enemies.changeTeam(newName)

    turnCalculator(usedEnemiesDict)

def createEnemy(enemyName, enemyData): #Creates enemy
    onLine = 0 if "onLine" not in enemyData else enemyData["onLine"] if not isinstance(enemyData["onLine"], list) else random.randint(enemyData["onLine"][0], enemyData["onLine"][1])
    enemyToAdd = customEnemies[enemyName]
    enemyToAdd["onLine"] = onLine

    return enemies(customEnemies[enemyName])

def turnCalculator(enemyDict): #Calculates turns of every person based on speed
    turnList = {}
    for character in characters.onTeam:
        turnList[character] = [characterDict[character].checkStat("speed"), "character"]
        
    for enemy in enemies.onTeam:
        turnList[enemy] = [enemyDict[enemy].checkStat("speed"), "enemy"]

    temp = list(turnList.items())
    temp.sort(key=lambda a: a[1][0], reverse=True)    
    turnList = dict(temp)

#--------------------------------------------------------------------------------Dialogue system stuff

class npc: #Npc which can be recruited, talked to or bought things from
    def __init__(self, characterInfo):
        self.name = characterInfo["name"]
        self.currentDialogue = characterInfo["currentDialogue"]
        self.possibleDialogue = characterInfo["possibleDialogue"]
        self.emotions = {
            "anger": 0,
            "happiness": 0,
            "sadness": 0
        } if not characterInfo["emotions"] else characterInfo["emotions"]
        self.recruitStats = characterInfo["recruitStats"] if "recruitStats" in characterInfo["recruitStats"] else None
        self.recruitCriteria = characterInfo["recruitCriteria"] if "recruitCriteria" in characterInfo["recruitCriteria"] else None

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

#--------------------------------------------------------------------------------Settings

def openSettingsMenu(): #Opens settings menu
    theContentDestroyer9000(content, deleteAll=True)
    contentCreator([
        ["button", [
            {"data": ["Exit", "loadCampaign", ""]}, 
            {"data": ["Current region", "currentRegion"]}, 
            {"data": ["Inventory", "intoInventory"]},
            {"data": ["Change party lines", "changePartyLine"]}
        ]]
    ])

#--------------------------------------------------------------------------------Main menu stuff

def mainMenu(): #Shows main menu
    contentCreator([
        ["button", [
            {"data": ["New game", "newGame"]}, {"data": ["Load save", "loadSave"]}, {"data": ["Delete save", "deleteSave"]}
        ]]
    ])

def newGame(): #Asks what campaign the player would like to start
    contentCreator([
        ["choice", [
            {"data": [x, x]} for x in campaigns.keys()
        ]],
        ["button", [{"data": ["Choose campaign", "chooseCharacter"]}]]
    ])

def chooseCharacter(): #Asks what character the player wants to play
    global currentCampaign
    if playerAnswer.get():
        currentCampaign = playerAnswer.get()
        contentCreator([
            ["choice", [
                {"data": [x, x]} for x in playableCharacters[currentCampaign].keys()
            ]],
            ["button", [{"data": ["Choose character", "loadCampaign"]}]]
        ], True)
    else:
        raise ValueError("Please select a campaign")

def loadCampaign(startNew=False): #Starts that campaign
    if startNew:
        if playerAnswer.get():
            addToCharacterDict(playableCharacters[currentCampaign][playerAnswer.get()])
            contentCreator([["button", [{"data": ["Settings", "openSettingsMenu", ""]}]]])
            nextRoom({playerAnswer.get(): ["goTo", list(campaigns[currentCampaign].keys())[0], 0]})
        else:
            raise ValueError("Please select character")
    else:
        if "talkTo" in currentRegionExtra.keys():
            talkTo(currentRegionExtra["talkTo"])
        elif "base" in currentRegionExtra.keys():
            goToBase()
        else:
            backToCampaign()

#--------------------------------------------------------------------------------Automatic function execution

def funcExecute(functionToUse, extraData=None): #executes whatever function we put into it. useful for dynamically creating buttons
    if functionToUse in list(functionList.keys()):
        functionList[functionToUse](extraData) if extraData else functionList[functionToUse]()

functionList = {
    "nextRoom": nextRoom,
    "newGame": newGame,
    "chooseCharacter": chooseCharacter,
    "loadCampaign": loadCampaign,
    "openSettingsMenu": openSettingsMenu,
    "addToTeamMenu": addToTeamMenu,
    "addToTeam": addToTeam,
    "removeFromTeamMenu": removeFromTeamMenu,
    "removeFromTeam": removeFromTeam,
    "backToCampaign": backToCampaign
}

#--------------------------------------------------------------------------------Not catagorized yet

def turnToNumber(value): #This is obsolete but im keeping it just to be sure
    try:
        value = float(value)
    except TypeError:
        return value
    finally:
        return value

def talkTo(character): #Open dialogue menu (can also include shop)
    pass

def savePosition(): #Save run data
    pass

def checkIfHasAchievement(toCheck, needsAll=False): #Checks if the player has achieved certain conditions (with the exception of npc emotions)
    hasAll = True
    for key in toCheck:
        if key == "hasItem":
            for item in toCheck["hasItem"]: #This should loop through all characters within the team
                for character in characterDict:
                    if characterDict[character].checkHasItem(item[0] if isinstance(item, list) else item, "not" if isinstance(item, list) else "has"):
                        if not needsAll:
                            return True
                    elif needsAll:
                        hasAll = False
                        break
        elif key == "onTeam":
            for character in toCheck["onTeam"]: #Checks if a given npc is on the players team
                if character in characters.onTeam or isinstance(character, list) and character[0] not in characters.onTeam:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break
        elif key == "defeatedBoss":
            for boss in toCheck["defeatedBoss"]: #Checks if the player has defeated a given boss
                if boss in playerAccomplishments["defeatedBosses"] or isinstance(boss, list) and boss[0] not in playerAccomplishments["defeatedBosses"]:
                    if not needsAll:
                        return True
                elif needsAll:
                    hasAll = False
                    break

#--------------------------------------------------------------------------------Start of game

mainMenu()

mainWindow.mainloop()