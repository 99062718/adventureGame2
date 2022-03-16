import json, os.path, tkinter
from tkinter import messagebox

def getParent(path, levels):
    current_directory = os.path.dirname(__file__)

    parent_directory = current_directory
    for i in range(0, levels):
        parent_directory = os.path.split(parent_directory)[0]

    file_path = os.path.join(parent_directory, path)
    return file_path

with open(getParent("gameData/customItems.json", 1), "r") as file:
    customItems = json.load(file)

class person: #Creates class from which characters and enemies inherit
    bodyparts = ["left", "right", "head", "chest", "legs", "feet", "amulet"]

    def __init__(self, characterData, loadFromSave=False):
        self._characterStats = {
            "name": characterData["name"],
            "health": characterData["health"],
            "maxHealth": characterData["maxHealth" if characterData.get("maxHealth") else "health"],
            "mana": characterData["mana"],
            "maxMana": characterData["maxMana"] if characterData.get("maxMana") else characterData["mana"],
            "attacks": characterData["attacks"] if characterData.get("attacks") else [],
            "attackMulti": characterData["attackMulti"] if characterData.get("attackMulti") else 1,
            "speed": characterData["speed"] if characterData.get("speed") else 1,
            "defense": characterData["defense"] if characterData.get("defense") else 1,
            "onLine": characterData["onLine"] if characterData.get("onLine") else 0,
            "equippedItems": {bodypart: characterData["equippedItems"].get(bodypart) for bodypart in self.bodyparts},
            "lifeSteal": characterData["lifeSteal"] if characterData.get("lifeSteal") else 0,
            "dmgOverTime": characterData["dmgOverTime"] if characterData.get("dmgOverTime") else []
        }

        if not loadFromSave:
            for bodyPart, item in self._characterStats["equippedItems"].items():
                if item:
                    self.changeItemModifyer(item)


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

        self.adjustStat(statToChange)
        
    def adjustStat(self, statToChange): #Adjusts stat when a certain value has been reached
        if statToChange in ["mana", "maxMana", "health", "maxHealth"]:
            if self.checkStat("health") > self.checkStat("maxHealth"):
                self.changeStat("set", "health", self.checkStat("maxHealth"))
            
            if self.checkStat("mana") > self.checkStat("maxMana"):
                self.changeStat("set", "mana", self.checkStat("maxMana"))
        
        if self._characterStats.get("currentAttack") and self._characterStats["currentAttack"] == len(self.checkStat("attacks")):
            self.changeStat("set", "currentAttack", 0)

    def checkStat(self, statToCheck): #Checks value of given stat
        if statToCheck in self._characterStats:
            return self._characterStats[statToCheck]
        else:
            raise ValueError(f"{statToCheck} is not an existing stat")

    def setItem(self, bodyPart, item): #Sets item of given bodypart
        pastItem = self.checkItem(bodyPart)
        if pastItem:
            self.changeItemModifyer(pastItem, True)
            characters.teamEquiped.remove(pastItem)
            characters.inventory.append(pastItem)

        self._characterStats["equippedItems"][bodyPart] = item

        if item:
            self.changeItemModifyer(item)
            if self.checkStat("team") == "character":
                characters.teamEquiped.append(item)
                characters.inventory.remove(item)

    def checkItem(self, bodyPart):
        return self._characterStats["equippedItems"][bodyPart]

    def changeItemModifyer(self, item, remove=False): #Adds or removes item modifyer from person stats
        for modifier, value in customItems[item].items():
            match modifier: #Gives an error in my IDE. Works perfectly though...
                case ("maxHealth" | "attackMulti" | "speed" | "maxMana" | "lifeSteal" | "defense"):
                    self.changeStat("subtract" if remove else "add", modifier, value)
                case "dmgOverTime":
                    for overTimeModifier in value:
                        self.changeStat("remove" if remove else "append", "dmgOverTime", overTimeModifier)

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

    def giveAllStats(self, dontShow=[]): #Creates string with all stats of person
        return "".join(f"{stat} - {value}\n" for stat, value in self._characterStats.items() if stat not in dontShow)

#-------------------------------------------------Characters

class characters(person): #Used for characters that have been recruited or are present within the team
    onTeam = []
    inventory = []
    teamEquiped = []
    currency = 0

    def __init__(self, characterData):
        super().__init__(characterData)
        self._characterStats["team"] = "character"
        self._characterStats["level"] = characterData["level"] if characterData.get("level") else 1
        self._characterStats["statScaling"] = characterData["statScaling"] if characterData.get("statScaling") else {}
        self._characterStats["xp"] = characterData["xp"] if characterData.get("xp") else 0
        self._characterStats["xpForNextLevel"] = characterData["xpForNextLevel"] if characterData.get("xpForNextLevel") else 10
        self._characterStats["toLearn"] = characterData.get("toLearn")
        for bodyPart, value in self._characterStats["equippedItems"].items(): #Adds all currently equipped items to inventory
            if value:
                characters.teamEquiped.append(value)

    @classmethod
    def checkHasItem(cls, item, notHas): #Should check if character has an item or not (not finished)
        if item in cls.inventory and notHas == "has" or item not in cls.inventory and notHas == "not" or item in cls.teamEquiped and notHas == "has" or item not in cls.teamEquiped and notHas == "not":
            return True
        return False

    def checkForLevelUp(self): #Level up functionality
        changebleStats = ["maxHealth", "maxMana", "attackMulti", "defense", "speed"]

        if self.checkStat("xp") >= self.checkStat("xpForNextLevel"):
            self.changeStat("set", "xp", self.checkStat("xp") % self.checkStat("xpForNextLevel"))
            self.changeStat("add", "level", 1)
            changedMessage = f"{self.checkStat('name')} leveled up!\nlevel: {self.checkStat('level')}\n"

            for toChange in changebleStats:
                oldStat = self.checkStat(toChange)
                changePercentage = self.checkStat("statScaling")[toChange] if self.checkStat("statScaling").get(toChange) else globalSettings["statScaling"][toChange]
                self.changeStat("set", toChange, round(oldStat * changePercentage))
                changedMessage += f"{toChange}: {oldStat} -> {self.checkStat(toChange)}\n"

            messagebox.showinfo(message=changedMessage)

            if self.checkStat("toLearn"):
                if str(self.checkStat("level")) in self.checkStat("toLearn"):
                    newlyLearned = []
                    for newAttack in self.checkStat("toLearn")[self.checkStat("level")]:
                        self.changeStat("append", "attacks", newAttack)
                        newlyLearned.append(newAttack)
                    messagebox.showinfo(message=f"{self.checkStat('name')} has learned the following attacks:\n".join(f"{attack}\n" for attack in newlyLearned))

#-------------------------------------------------Enemies

class enemies(person): #Used for enemies currently in battle with
    onTeam = []

    def __init__(self, characterData):
        super().__init__(characterData)
        self._characterStats["team"] = "enemy"
        self._characterStats["currentAttack"] = characterData["currentAttack"] if characterData.get("currentAttack") else 0

    def deleteSelf(self, name):
        enemies.onTeam.remove(name)
        del self

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

                if dialogue[0].get("subText"):
                    pass
                else:
                    if dialogue[0].get("relation"): #Checks emotion npc has for player
                        for emotion, value in dialogue[0]["relations"].items():
                            if self.emotions.get(emotion):
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

                    if dialogue[0].get("world"): #Checks achievements player has accomplished
                        if checkIfHasAchievement(dialogue[0]["world"], needsAll=True): #CheckIfHasAchievement does not work due to it being in the other file. Might have to move this class to the main file
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