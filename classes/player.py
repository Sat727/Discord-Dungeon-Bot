from classes.entity import Entity
class Player(Entity):
    def __init__(self, name, chosenclass, current_hp, max_hp, base_dps, xp, level, inventory:dict=None):
        super().__init__(name, max_hp, base_dps=base_dps)
        self.chosenclass = chosenclass
        self.name = name
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.base_dps = base_dps
        self.xp = xp
        self.level = level