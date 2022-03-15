import tkinter, random, json
from gameFunctions.classFunctions import *
from tkinter import StringVar, ttk, messagebox, IntVar
from tkinter.constants import OUTSIDE

#To do:
#Create room system (Very important!!)
# - Add extra settings that count for the entire campaign (such as party size limits)
# - Implement "goTo next" and defaults for choiceEvents
# - Losing battle should trigger save state if ifLose hasent been specified
#Create battle system (the line layer system) (Important)
# - Npcs and player attacks can be removed and added
# - Make enemies drop xp and gold once battle has been won
# - Base xp off of enemy healh
# - Base gold off potential damage enemy can do
#Level stuff
# - Scale can be given per character or per campaign
#Create npc dialogue system (Important)
# - Npcs should be able to get recruited based on certain criteria
# - Add possibility for shops
# - Attacks can be learned by buying them from a shop
# - Add ability to make certain choices open up new dialogue options
# - Talking to npc should bring up 3 dialogue choices (based on highest in currentDialogue hierarchy) + shop when thats available
#Create loot system (for things like gold for shops and items that can be picked up) (Lesser importance)
# - Gold and xp obtained from killing enemies should be a mix between random and set
#Support for multiple save files (Very imporant!!)
# - Reminder that obj.__dict__ is a thing
# - Battles are going to be a bit of a hard one. Save all enemies to currentRegionExtra and save that to json

#Ideas to flesh the game out a bit more:
#Items
# - Durability (dont have to be used for every item)
# - Consumables
# - Extra loot dropped (higher chance at enemy dropping their items or more gold)
# - Thing that happen depending on the percentage of health the player has (more attack, higher crit chance, more defense, ect)
# - Events that trigger when crit happens (Gain health when crit, gain money on crit, ect)
# - Items that are better against certain types of monsters
#Battle
# - Some kind of AOI attack that hits all enemies on a line (could also be crosslined)
# - Attack that hits a set of random enemies (for the gamblers among us)
#Bosses
# - Bosses might be able to drop special items that can only be obtained from them
#Rooms
# - Dungeons (this is to fix balancing for battles and xp as it is extremely difficult as is)
#Cheat codes
# - UNLIMITED POWAH
# - Max health
# - Max mana
# - Gain the most powerful weapon in all of existance
# - Die

mainWindow = tkinter.Tk()
mainWindow.configure(padx=50, pady=30)

#--------------------------------------------------------------------------------Dictionaries

characterDict = {}
playerAccomplishments = { #Add all player accomplishments (like beating a boss) to this
    "defeatedBosses": []
}
currentRegionExtra = {} #This is for keeping track of the player being in battle, base, or talking to an npc
content = [[], []]

#--------------------------------------------------------------------------------Characters

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
        ["button", [{"data": data} for data in (["Add to team", "addToTeamMenu"], ["Remove from team", "removeFromTeamMenu"], ["Exit base", "backToCampaign"])]]
    ])

def addToTeamMenu(): #Player can choose what character they want to add to their team
    if len(characters.onTeam) < len(characterDict):
        contentCreator([
            ["text", [{"data": ["Which character would you like to add to your party?"]}]],
            ["choice", [{"data": [character, character], "blockIf": {"onTeam": character}} for character in characterDict]],
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
            ["choice", [{"data": [character, character]} for character in characters.onTeam]],
            ["button", [{"data": ["Choose character", "removeFromTeam"]}, {"data": ["Back", "goToBase"]}]]
        ])
    else:
        messagebox.showerror(message="Characters cannot be removed while team size is 1!")

def removeFromTeam(): #Removes character from team and returns to base if succesful
     ifSuccesful = characters.changeTeam(playerAnswer.get(), "remove")
     if ifSuccesful:
         goToBase()

#--------------------------------------------------------------------------------Room generation

def roomTypeCheck(currentRoom): #Checks roomType of room
    if currentRoom["roomType"] == "normal":
        contentCreator(currentRoom["content"], currentRoom["choiceEvents"])
    elif currentRoom["roomType"] == "battle":
        battleInitializer(currentRoom["content"], currentRoom["choiceEvents"])
    else:
        raise ValueError(f"{currentRoom['roomType']} is not a valid roomType")

def nextRoom(data, pseudoAnswer=None): #Goes to next room
    global currentRegion
    answer = pseudoAnswer if pseudoAnswer else playerAnswer.get()
    if answer in data.keys():
        if data[answer][0] == "goTo": #Goes to given room (should also use saveData function)
            currentRegion = [data[answer][1], data[answer][2]]
            roomTypeCheck(campaigns[currentCampaign][currentRegion[0]][currentRegion[1]])
        elif data[answer][0] == "talkTo": #Goes into dialogue menu with npc
            talkTo(answer)
        elif data[answer][0] == "base": #Goes to player base
            goToBase()
    else:
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

    theContentDestroyer9000(content)

    for currentContent in roomContent:
        if currentContent[0] in ("choice", "textBox"):
            playerAnswer = StringVar()
        elif currentContent[0] == "numberBox":
            playerAnswer = IntVar(value=0)

        for currentText in currentContent[1]:
            if "blockIf" in currentText: #Checks if widget should be shown or not
                if checkIfHasAchievement(currentText["blockIf"]):
                    continue

            match currentContent[0]:        
                case "text": #Creates label
                    currentWidget = tkinter.Label(text=currentText["data"][0])
                case "choice": #Creates radio button       
                    currentWidget = ttk.Radiobutton(
                        text=currentText["data"][0],
                        value=currentText["data"][1],
                        variable=playerAnswer
                    )
                case "button": #Creates button
                    currentWidget = ttk.Button(
                        text=currentText["data"][0],
                        command=lambda toUse=currentText["data"][1], extraData=extraData if extraData else None: funcExecute(toUse, extraData) if extraData else funcExecute(toUse) #Turn this into a lambda function
                    )
                case "numberBox":
                    currentWidget = ttk.Spinbox(
                        from_=float("-inf"),
                        to=float("inf"),
                        textvariable=playerAnswer
                    )
                case _:
                    raise ValueError(f"{currentContent[0]} is not a valid widget")
            
            if len(currentText["data"]) < 3:
                currentWidget.grid(column=0, row=num, pady=5)
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

#-------------------------------------------------Creation

#The way i wrote this function just does not feel right...
def battleInitializer(roomContent, choiceEvents): #Innitiates battle
    global currentRegionExtra
    usedEnemiesDict = {}
    toCreate = {}
    enemies.onTeam = []
    currentRegionExtra["battle"] = {"bosses": []}

    if roomContent.get("boss"): #Checks for bosses
        for boss, bossData in roomContent["boss"].items():
            currentRegionExtra["battle"]["bosses"].append("boss")
            if toCreate.get(boss):
                toCreate[boss]["timesAppear"] += 1
            else:
                toCreate[boss] = bossData
                toCreate[boss]["timesAppear"] = 1

    if roomContent.get("enemies"): #Checks for enemies given outside template use
        for enemy, enemyData in roomContent["enemies"].items():
            toCreate[enemy] = enemyData
            toCreate[enemy]["timesAppear"] = calcTimesAppear(enemyData)
        
    if roomContent.get("templates"): #Checks for templates used
        for template in roomContent["templates"]:
            for enemy, enemyData in battleTemplates[template].items():
                if toCreate.get(enemy):
                    plusAppear = calcTimesAppear(enemyData)
                    toCreate[enemy]["timesAppear"] += plusAppear
                else:
                    toCreate[enemy] = enemyData
                    toCreate[enemy]["timesAppear"] = calcTimesAppear(enemyData)
    
    for enemyName, enemyData in toCreate.items(): #Goes through toCreate to make enemies
        if enemyData["timesAppear"] == 1:
            usedEnemiesDict[enemyName] = createEnemy(enemyName, enemyData)
            enemies.changeTeam(enemyName)
        else:
            for timesAppeared in range(enemyData["timesAppear"]):
                newName = f"{enemyName}{timesAppeared + 1}"
                usedEnemiesDict[newName] = createEnemy(enemyName, enemyData)
                enemies.changeTeam(newName)

    turnCalculator(usedEnemiesDict)

def calcTimesAppear(enemyData): #Calculates times a certain enemy will appear
    return 1 if "timesAppear" not in enemyData else enemyData["timesAppear"] if not isinstance(enemyData["timesAppear"], list) else random.randint(enemyData["timesAppear"][0], enemyData["timesAppear"][1])

def createEnemy(enemyName, enemyData): #Creates enemy
    onLine = 0 if "onLine" not in enemyData else enemyData["onLine"] if not isinstance(enemyData["onLine"], list) else random.randint(enemyData["onLine"][0], enemyData["onLine"][1])
    enemyToAdd = customEnemies[enemyName]
    enemyToAdd["onLine"] = onLine

    return enemies(customEnemies[enemyName])

#-------------------------------------------------Turn logic

def turnCalculator(enemyDict): #Calculates turns of every person based on speed
    turnList = []
    for character in characters.onTeam:
        turnList.append([character, characterDict[character].checkStat("speed"), "character"])
        
    for enemy in enemies.onTeam:
        turnList.append([enemy, enemyDict[enemy].checkStat("speed"), "enemy"])

    turnList.sort(key=lambda a: a[1], reverse=True)
    turnInnitializer(turnList, enemyDict, 0)

def turnInnitializer(turnList, enemyDict, turnNum): #Checks everything turn related
    global currentRegionExtra, playerAccomplishments
    currentRegionExtra["battle"] = {"enemies": enemyDict, "turn": turnNum, "turns": turnList, "bosses": currentRegionExtra["battle"]["bosses"]}

    aliveCharacters = [character[0] for character in turnList if character[2] == "character" and characterDict[character[0]].checkStat("health") > 0]
    aliveEnemies = [enemy[0] for enemy in turnList if enemy[2] == "enemy" and enemyDict[enemy[0]].checkStat("health") > 0]

    if not aliveCharacters: #Should trigger ifLose
        if campaigns[currentCampaign][currentRegion[0]][currentRegion[1]]["choiceEvents"].get("ifLose"):
            returnAllToMax()
            return nextRoom(campaigns[currentCampaign][currentRegion[0]][currentRegion[1]]["choiceEvents"], "ifLose")
    elif not aliveEnemies: #Should trigger ifWin
        returnAllToMax()

        if currentRegionExtra["battle"].get("bosses"): #Adds bosses to playerAccomplishments if any defeated
            for boss in currentRegionExtra["battle"]["bosses"]:
                if boss not in playerAccomplishments["defeatedBosses"]:
                    playerAccomplishments["defeatedBosses"].append(boss)

        return nextRoom(campaigns[currentCampaign][currentRegion[0]][currentRegion[1]]["choiceEvents"], "ifWin")

    if turnNum >= len(turnList):
        return turnCalculator(enemyDict)

    if turnList[turnNum][2] == "enemy" and enemyDict[turnList[turnNum][0]].checkStat("health") > 0:
        enemyAttack(turnList[turnNum][0])
    elif turnList[turnNum][2] == "character" and characterDict[turnList[turnNum][0]].checkStat("health") > 0:
        chooseEnemy(turnList[turnNum][0])
    else:
        turnInnitializer(turnList, enemyDict, turnNum + 1)

#-------------------------------------------------Enemy logic

def enemyAttack(attacker): #Enemy attack oOoooOOooOooOOOO
    enemyDict = currentRegionExtra["battle"]["enemies"]
    attackable = [[character, characterDict[character].checkStat("onLine")] for character in characters.onTeam if characterDict[character].checkStat("health") > 0]
    attackable.sort(key=lambda a: a[1])
    toAttack = attackable[0][0]

    while True:
        attack = enemyDict[attacker].checkStat("attacks")[enemyDict[attacker].checkStat("currentAttack")]
        if customAttacks[attack].get("mana"):
            if customAttacks[attack]["mana"] > enemyDict[attacker].checkStat("mana"):
                enemyDict[attacker].changeStat("add", "currentAttack", 1)
                continue
            else:
                enemyDict[attacker].changeStat("subtract", "mana", customAttacks[attack]["mana"])
        break

    attackDMG = round(customAttacks[attack]["damage"] * enemyDict[attacker].checkStat("attackMulti") / characterDict[toAttack].checkStat("defense"))
    lifeSteal = (customAttacks[attack].get("lifeSteal") if customAttacks[attack].get("lifeSteal") else 0) + enemyDict[attacker].checkStat("lifeSteal")
    lifeStealValue = (100 if lifeSteal > 100 else lifeSteal) * attackDMG / 100

    characterDict[toAttack].changeStat("subtract", "health", attackDMG)
    enemyDict[attacker].changeStat("add", "health", lifeStealValue)
    enemyDict[attacker].changeStat("add", "currentAttack", 1)

    attackerName = enemyDict[attacker].checkStat("name")

    printAttack([
        f"{attackerName} used {attack} on {toAttack} for {attackDMG} damage!", 
        f"{attackerName} healed {lifeStealValue} from life steal" if lifeSteal else None, 
        f"{toAttack} has died!" if characterDict[toAttack].checkStat("health") <= 0 else None
    ])

    turnInnitializer(currentRegionExtra["battle"]["turns"], enemyDict, currentRegionExtra["battle"]["turn"] + 1)

#-------------------------------------------------Player logic

def chooseEnemy(name): #Shows menu for attacking enemies
    enemyDict = currentRegionExtra["battle"]["enemies"]
    onLineEnemies = [[enemy, enemyData.checkStat("onLine")] for enemy, enemyData in enemyDict.items() if enemyData.checkStat("health") > 0]
    onLineEnemies.sort(key=lambda a: a[1])
    attackable = [enemy for enemy in onLineEnemies if enemy[1] == onLineEnemies[0][1]]

    data = {"enemies": enemyDict, "attacker": name}
    contentCreator([
        ["text", [{"data": [f"It's {name}'s turn!"]}, {"data": ["Who will you attack?"]}]],
        ["choice", [{"data": [enemyDict[enemy[0]].checkStat("name"), enemy[0]]} for enemy in attackable]],
        ["button", [{"data": ["Choose enemy", "chooseAttack"]}]]
    ], data)

def chooseAttack(data): #Shows menu for attacks to use
    if playerAnswer.get():
        data["toAttack"] = playerAnswer.get()
        contentCreator([
            ["text", [{"data": ["What attack will you use?"]}]],
            ["choice", [{"data": [attack, attack]} for attack in characterDict[data["attacker"]].checkStat("attacks")]],
            ["button", [{"data": ["Choose attack", "playerAttack"]}]]
        ], data)

def playerAttack(data): #Logic for player attacks
    global currentRegionExtra

    if playerAnswer.get():
        if customAttacks[playerAnswer.get()].get("mana"):
            if customAttacks[playerAnswer.get()]["mana"] > characterDict[data["attacker"]].checkStat("mana"):
                messagebox.showerror(message="You dont have enough mana to do this attack!")
                return
            characterDict[data["attacker"]].changeStat("subtract", "mana", customAttacks[playerAnswer.get()]["mana"])

        attackDMG = round(customAttacks[playerAnswer.get()]["damage"] * characterDict[data["attacker"]].checkStat("attackMulti") / data["enemies"][data["toAttack"]].checkStat("defense"))
        lifeSteal = (customAttacks[playerAnswer.get()].get("lifeSteal") if customAttacks[playerAnswer.get()].get("lifeSteal") else 0) + characterDict[data["attacker"]].checkStat("lifeSteal")
        lifeStealValue = (100 if lifeSteal > 100 else lifeSteal) * attackDMG / 100

        data["enemies"][data["toAttack"]].changeStat("subtract", "health", attackDMG)
        characterDict[data["attacker"]].changeStat("add", "health", lifeStealValue)

        enemyName = data["enemies"][data["toAttack"]].checkStat("name")
        
        printAttack([
            f"{data['attacker']} used {playerAnswer.get()} on {enemyName} for {attackDMG} damage!", 
            f"{data['attacker']} healed {lifeStealValue} from life steal" if lifeSteal else None, 
            f"{enemyName} has died!" if data["enemies"][data["toAttack"]].checkStat("health") <= 0 else None
        ])

        if data["enemies"][data["toAttack"]].checkStat("health") <= 0:
            data["enemies"][data["toAttack"]].deleteSelf(data["toAttack"])

        currentRegionExtra["battle"]["turn"] += 1
        loadCampaign()

#-------------------------------------------------Uncatagorised

def printAttack(toPrint): #Prints events happening during attack
    for text in toPrint:
        if text:
            messagebox.showinfo(message=text)

def returnAllToMax():
    for name, character in characterDict.items():
        character.changeStat("set", "health", character.checkStat("maxHealth"))
        character.changeStat("set", "mana", character.checkStat("maxMana"))

#--------------------------------------------------------------------------------Settings

#-------------------------------------------------General menus

def openSettingsMenu(): #Opens settings menu
    theContentDestroyer9000(content, deleteAll=True)
    contentCreator([
        ["button", [{"data": data} for data in (["Exit", "loadCampaign", ""], ["Current region", "printRegion"], ["Inventory", "intoInventory"], ["Change party lines", "changePartyLineMenu"], ["Check character stats", "checkCharacterMenu"])]]
    ])

def showTeamList(data): #Shows list of characters that can be chosen
    if playerAnswer.get() or data.get("forceShow"):
        if data.get("functionality") == "add":
            data["item"] = playerAnswer.get()

        contentCreator([
            ["text", [{"data": ["Choose a character"]}]],
            ["choice", [{"data": [character, character]} for character in characterDict]],
            ["button", [{"data": ["Choose character", data["menu"]]}]]
        ], data)

#-------------------------------------------------Region printer

def printRegion():
    messagebox.showinfo(message=f"Your current region is: {currentRegion[0]}")

#-------------------------------------------------Inventory

def intoInventory(): #Opens inventory menu
    contentCreator([
        ["text", [{"data": [text]} for text in ("Welcome to the inventory!", "What is it you want to do?")]],
        ["choice", [{"data": data} for data in (["Remove item from character", "remove"], ["Add item to character", "add"], ["Check item stat", "stat"])]],
        ["button", [{"data": ["Choose functionality", "showInventoryItemList"]}]]
    ])

def showInventoryItemList(): #Shows list of items that can be chosen
    if playerAnswer.get() == "remove":
        return showTeamList({"functionality": playerAnswer.get(), "menu": "chooseBodypart"})

    if playerAnswer.get():
        text = playerAnswer.get() if playerAnswer.get() == "add" else "check stat of"

        contentCreator([
            ["text", [{"data": [f"Choose an item to {text}:"]}]],
            ["choice", [{"data": [item, item]} for item in characters.inventory]],
            ["button", [{"data": ["Choose item", "executeItemFunc" if playerAnswer.get() == "stat" else "showTeamList"]}]]
        ], {"functionality": playerAnswer.get(), "menu": "chooseBodypart"})

def chooseBodypart(data): #Choose bodypart to add/remove item from
    if playerAnswer.get():
        data["character"] = playerAnswer.get()
        choiceArray = [{"data": [f"{bodypart} - {item}", bodypart]} for bodypart, item in characterDict[data["character"]].checkStat("equippedItems").items() if item] if data["functionality"] == "remove" else [{"data": [f"{bodypart} - {item}", bodypart]} for bodypart, item in characterDict[data["character"]].checkStat("equippedItems").items() if bodypart in customItems[data["item"]]["bodyparts"]]
        contentCreator([
            ["text", [{"data": ["Choose a bodypart to edit item of:"]}]],
            ["choice", choiceArray],
            ["button", [{"data": ["Choose bodypart", "executeItemFunc"]}]]
        ], data)

def executeItemFunc(data): #adds/removes items from character or checks item stat
    if playerAnswer.get():
        if data["functionality"] == "add":
            characterDict[data["character"]].setItem(playerAnswer.get(), data["item"])
        elif data["functionality"] == "remove":
            characterDict[data["character"]].setItem(playerAnswer.get(), None)
        else:
            text = "".join([f"{modifier}: {value}\n" for modifier, value in customItems[playerAnswer.get()].items()])
            messagebox.showinfo(message=text)
        openSettingsMenu()

#-------------------------------------------------Line changer

def changePartyLineMenu(): #Opens showTeamList with insertLine as button function
    showTeamList({"menu": "insertLine", "forceShow": True})

def insertLine(data): #Player must enter line they want character on here
    if playerAnswer.get():
        playerAnswer.get()
        contentCreator([
            ["text", [{"data": [f"Enter a line to put {playerAnswer.get()} on:"]}]],
            ["numberBox", [{"data": []}]],
            ["button", [{"data": ["Choose line", "putOnLine"]}]]
        ], playerAnswer.get())

def putOnLine(character): #Puts chosen character on chosen line
    if playerAnswer.get():
        characterDict[character].changeStat("set", "onLine", playerAnswer.get())
        openSettingsMenu()

#-------------------------------------------------Character stats

def checkCharacterMenu():
    showTeamList({"menu": "showStats", "forceShow": True})

def showStats(data):
    if playerAnswer.get():
        info = characterDict[playerAnswer.get()].giveAllStats(["team", "statScaling", "toLearn", "dmgOverTime"])
        messagebox.showinfo(message=info)
        openSettingsMenu()

#--------------------------------------------------------------------------------Main menu stuff

def mainMenu(): #Shows main menu
    contentCreator([["button", [{"data": data} for data in (["New game", "newGame"], ["Load save", "loadSave"], ["Delete save", "deleteSave"])]]])

def newGame(): #Asks what campaign the player would like to start
    contentCreator([
        ["choice", [{"data": [x, x]} for x in campaigns.keys()]],
        ["button", [{"data": ["Choose campaign", "chooseCharacter"]}]]
    ])

def chooseCharacter(): #Asks what character the player wants to play
    global currentCampaign
    if playerAnswer.get():
        currentCampaign = playerAnswer.get()
        contentCreator([
            ["choice", [{"data": [x, x]} for x in playableCharacters[currentCampaign].keys()]],
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
        if currentRegionExtra.get("talkTo"):
            talkTo(currentRegionExtra["talkTo"])
        elif currentRegionExtra.get("base"):
            goToBase()
        elif currentRegionExtra.get("battle"):
            theContentDestroyer9000(content, deleteAll=True)
            contentCreator([["button", [{"data": ["Settings", "openSettingsMenu", ""]}]]])
            turnInnitializer(currentRegionExtra["battle"]["turns"], currentRegionExtra["battle"]["enemies"], currentRegionExtra["battle"]["turn"])
        else:
            backToCampaign()

#--------------------------------------------------------------------------------Json file reading

def checkGameData(): #Reads campaigns, playableCharacters, battleTemplates, customItems, customEnemies and customAttacks .json files
    global campaigns, battleTemplates, customAttacks, customEnemies, customItems, playableCharacters
    files = ["campaigns", "battleTemplates", "customAttacks", "customEnemies", "customItems", "playableCharacters"]
    data = {}
    for currentFile in files:
        with open(f"gameData/{currentFile}.json", "r") as openedFile:
            data[currentFile] = json.load(openedFile)
    
    campaigns = data["campaigns"]
    battleTemplates = data["battleTemplates"]
    customAttacks = data["customAttacks"]
    customEnemies = data["customEnemies"]
    customItems = data["customItems"]
    playableCharacters = data["playableCharacters"]

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
    "showTeamList": showTeamList,
    "printRegion": printRegion,
    "intoInventory": intoInventory,
    "showInventoryItemList": showInventoryItemList,
    "chooseBodypart": chooseBodypart,
    "executeItemFunc": executeItemFunc,
    "changePartyLineMenu": changePartyLineMenu,
    "insertLine": insertLine,
    "putOnLine": putOnLine,
    "checkCharacterMenu": checkCharacterMenu,
    "showStats": showStats,
    "addToTeamMenu": addToTeamMenu,
    "addToTeam": addToTeam,
    "removeFromTeamMenu": removeFromTeamMenu,
    "removeFromTeam": removeFromTeam,
    "backToCampaign": backToCampaign,
    "chooseAttack": chooseAttack,
    "playerAttack": playerAttack
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
                if characters.checkHasItem(item[0] if isinstance(item, list) else item, "not" if isinstance(item, list) else "has"):
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

checkGameData()
mainMenu()

mainWindow.mainloop()