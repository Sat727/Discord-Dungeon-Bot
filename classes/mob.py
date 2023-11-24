from abc import ABC, abstractmethod
from classes.entity import Entity




#Types for Mobs
# 0 = None
# 1 = Life
# 2 = Fire
# 3 = Death 
# 4 = Mythical
# 5 = Storm
# 6 = Ice
# PLACEHOLDER

class Mob(Entity):
    elite = False
    weapon = None
    def __init__(self, name, max_hp, xp_gain, base_dps, type, drops=None, weapon=None):
        super().__init__(name, max_hp, base_dps)
        self.name = name
        self.hp = max_hp
        self.max_hp = max_hp
        self.xp_gain = xp_gain
        self.base_dps = base_dps
        self.drops = drops
        self.type = type
        self.weapon = weapon





mobs = {
    "Goblin": 
        Mob("Goblin", 150, 5, 10, 4),
    "Troll":
        Mob("Troll", 200, 5, 20, 4),
    "Skeleton Mage": 
        Mob("Skeleton Mage", 76, 10, 30, 3),
    "Treent":
        Mob("Treent", 200, 5, 20, 1),
    "Ice Wraith": 
        Mob("Ice Wraith", 75, 5, 20, 6)
}
