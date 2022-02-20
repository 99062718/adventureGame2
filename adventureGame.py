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
#Create npc dialogue system (Normal importance)
# - Npcs should be able to get recruited based on certain criteria
# - Npcs recruited can be put inside or removed from the team
#Create inventory system (Lesser imporance)
# - Items can be equipped from here
#Create item support for characters (Normal importance)
# - Items can give special bonusses like +atk, +def or +agility but can also give special bonusses like extra attack done to wolf enemies
# - Items maybe can have a kind of debuff attached to them like -2 def or extra damage taken from wolf enemies
#Create loot system (for things like gold for shops and items that can be picked up) (Lesser importance)
# - Bosses might be able to drop special items that can only be obtained from them
# - Gold obtained from killing enemies should be a mix between random and set
#Create options menu with current zone, health, cheatcodes, ect (Important)
#Support for multiple save files (Very imporant!!)
#Support for multiple campaigns (which can all have multiple characters) (Very Important!!)
#Implement checkHasItem in character class
#Create dict with all thus far recruited members. Also make a list in which all names of members that are currently in the party reside
#Create dict with players accomplishments (did quest, beat boss, ect)

class characters:
    def __init__(self, name, health, attacks=None, items=None):
        self.__characterStats = {
            "name": name,
            "health": health,
            "maxHealth": health,
            "attacks": attacks if attacks != None else {},
            "items": items if items != None else {}
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
        if statToCheck in __characterStats:
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

def contentCreator(roomContent, noOptions=False):
    for currentContent in roomContent:
        if currentContent[0] == "text":
            for currentText in currentContent[1]:
                print(currentText)
        elif currentContent[0] == "choice":
            choiceInput(currentContent[1], noOptions)
        else:
            raise ValueError(f"{currentContent[0]} is not a valid widget")

def choiceInput(choices, noOptions):
    choicesToPrint = []

    for choice in choices:
        showChoice = True
        if "blockIf" in choice:
            for key in choice["blockIf"]:
                if key == "hasItem":
                    for item in choice["blockIf"]["hasItem"]: #This should loop through all characters within the team
                        if checkHasItem(item[0], "not" if isinstance(item, array) else "has"):
                            showChoice = False
                            break
                elif key == "onTeam":
                    for character in choice["blockIf"]["onTeam"]:
                        if character in playerTeam or isinstance(character, array) and character not in playerTeam:
                            showChoice = False
                            break
                elif key == "defeatedBoss":
                    for boss in choice["blockIf"]["defeatedBoss"]:
                        if boss in playerAccomplishments["defeatedBosses"] or isinstance(boss, array) and boss not in playerAccomplishments["defeatedBosses"]:
                            showChoice = False
                            break
                else:
                    raise ValueError(f"{key} is not a valid blockIf state")

        if showChoice:
            choicesToPrint.append(choice)

    while True:
        for loopNum, choice in enumerate(choicesToPrint):
            print(f"{loopNum + 1}. {choice[0]}")
        playerInput = input("Which one do you choose?\n").lower()
        playerInput = turnToNumber(playerInput)
        if isinstance(playerInput, float) and playerInput <= len(choicesToPrint):
            return choicesToPrint[playerInput - 1]["data"][1]
        elif playerInput == "options" and not noOptions:
            optionsMenu()
        else:
            print(f"{playerInput} is not a valid choice")

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