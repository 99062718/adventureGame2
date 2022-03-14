import json, sys, os.path

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
            "attacks": characterData["attacks"] if characterData.get("attacks") else [],
            "attackMulti": characterData["attackMulti"] if characterData.get("attackMulti") else 1,
            "speed": characterData["speed"] if characterData.get("speed") else 1,
            "defense": characterData["defense"] if characterData.get("defense") else 1,
            "mana": characterData["mana"],
            "maxMana": characterData["maxMana"] if characterData.get("maxMana") else characterData["mana"],
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
            if self.checkStat("name") in characterDict.keys():
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

#-------------------------------------------------Characters

class characters(person): #Used for characters that have been recruited or are present within the team
    onTeam = []
    inventory = []
    teamEquiped = []

    def __init__(self, characterData):
        super().__init__(characterData)
        self._characterStats["level"] = characterData["level"] if characterData.get("level") else 1
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

#-------------------------------------------------Enemies

class enemies(person): #Used for enemies currently in battle with
    onTeam = []

    def __init__(self, characterData):
        super().__init__(characterData)
        self._characterStats["currentAttack"] = characterData["currentAttack"] if characterData.get("currentAttack") else 0

    def deleteSelf(self, name):
        enemies.onTeam.remove(name)
        del self