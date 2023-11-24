from classes.mob import Mob, mobs
from classes.player import Player
from classes.weapons import Weapon
from classes. entity import Entity
import discord
import random
import math
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, HybridCommand
#player = Player(250, 250, 25, 0, 1)
def AliveCheck(entity):
    return entity.hp > 0
class Game():
    def __init__(self, player:Player, mob1:Mob, embed:discord.Embed):
        self.player = player
        self.moblist = mob1
        self.embed = embed
        
    async def attack(self, interaction:discord.Interaction, attacker:Entity, selected:list):    
        def CalculateEntityDamage(ent:Entity):
            damage = math.floor(random.randrange(7, 9) * 0.1 * ent.base_dps)
            if ent.weapon:
                damage += ent.weapon.damage
            return damage
        conc = '\nPlayer Turn:\n'
        for i in selected: 
            # Calculate damange and critical modifier here
            dmg = CalculateEntityDamage(attacker)
            self.moblist[i].hp -= dmg
            conc += f"{attacker.name} attacked {self.moblist[i].name} dealt {dmg} damage\n"
        conc += '\nMob Turn:\n'
        Alive = [x for x in self.moblist if AliveCheck(x)]
        #if len(Alive) == 0:
        #    return False
        for i in Alive:
            dmg = CalculateEntityDamage(i)
            self.player.current_hp -= dmg
            conc += f"{i.name} attacked {attacker.name} dealt {dmg} damage\n"
        self.embed.description = f"Health: {self.player.current_hp}/{self.player.max_hp}"
        self.embed.title= f"{self.player.name} (Level {self.player.level} {self.player.chosenclass})"
        if Alive == []:
            print("All mobs dead")
            return False
        if self.player.current_hp <= 0:
            print("Player died")
            return True
        self.embed.clear_fields()
        for mob in self.moblist:
            self.embed.add_field(name=f"{mob.name}",value=f"{mob.hp}/{mob.max_hp}")
        self.embed.set_footer(text=conc)
        # test = ["1","2","3"]
        # self.embed.set_footer(text=f"You hit {[i for i in test]} with {attacker.base_dps}".strip("[").strip("'").strip("]"))
        await interaction.message.edit(embed=self.embed)
        try:
            await interaction.response.defer()
        except:
            pass

    async def flee(self, interaction:discord.Interaction):
        if self.player.hp < self.player.hp * 0.25:
            await interaction.followup.send(content="You cannot flee when under 25% health.")
