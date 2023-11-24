class Entity():
    def __init__(self, name, max_hp, base_dps=10, weapon=None):
        self.name = name
        self.hp = max_hp
        self.base_dps = base_dps
        self.weapon = weapon