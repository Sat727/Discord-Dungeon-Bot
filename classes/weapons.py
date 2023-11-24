from classes.items import Items
from functools import wraps
import inspect

class Weapon(Items):
    def __init__(self, name, damage, value, element, critmultiplier):
        self.name = name
        self.damage = damage
        self.value = value
        self.element = element
        self.critmultifier = critmultiplier
        super().__init__(name, value, equiptable=True)
    











placeholderitems = {
    "Rusty Sword": {
        "Name": "Rusty Sword",
        "Damage": 2,
        "Value": 10,
        "Element": 1,
        "CritChance": 0.01,
    }
}


#Testweapon = Weapon(placeholderitems.values())


