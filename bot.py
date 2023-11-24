import json
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, HybridCommand
import sqlite3
from copy import copy
from discord import app_commands
import os
import sys
import asyncio
import random
import typing
import itertools
from discord.interactions import Interaction
from classes.mob import Mob, mobs
from classes.player import Player
from classes.weapons import Weapon
from classes.game import Game
import sqlite3
from collections import OrderedDict
from functools import partial
from typing import Any
import time
conn = sqlite3.connect("characters.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS characters(ID, Name, Class, CurrentHP, BaseDPS, Weapon, Level, Xp, XPCap, CriticalChance, Inventory)")
again = 'Press button below to return play again.'
class aclient(discord.Client):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
        print('Logged in')

client = aclient()
tree = app_commands.CommandTree(client)

class InteractionCheck(discord.ui.View):
    def __init__(self, message:discord.Interaction):
        self.msg = message
        super().__init__()

    async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
        if inter.user.id != self.msg.user.id:
            await inter.response.send_message(content="You don't have permission to press this button.", ephemeral=True)
            return False
        return True

# name, current_hp, max_hp, damage, xp, level, inventory:dict=None):

# Starting classes, Should be added to it's own database to incluse abilities in the future

StartingClasses = {
             "Rogue":
                 ("Rogue", 150, 150, 20, 0, 1, 0, 100, 0),
             "Wizard":
                 ("Wizard", 175, 175, 30, 0, 1, 0, 100, 0),
             "Warrior": 
                 ("Warrior", 250, 250, 50, 0, 1, 0, 100, 0)
                     }

def GenStats(dcid):
    Conc = ''
    cur.execute(f"select * from characters where id = ?", (dcid,))
    for i in [i for i in cur.description if i != None]:
        cur.execute(f"SELECT {i[0]} FROM characters")
        Conc += f"{i[0]}: ```{cur.fetchone()[0]}```\n"
    return Conc



def AliveCheck(entity):
    return entity.hp > 0



def CharCheck(DiscordId):
    char = cur.execute("SELECT * FROM characters WHERE id=?", (DiscordId,))
    char = char.fetchall()
    if char != []:
        return char
    else:
        return None

def AssignPlayer(DiscordId):
    player = CharCheck(DiscordId)[0]
    return Player(player[1], player[2], player[3], player[3], player[4], player[5], player[6])

def HomeEmbed(Char:Player): # TODO Add what world they are currently in
    embed = discord.Embed(title=f"{str(Char.name)}", description=f"Level {Char.level} {Char.chosenclass}")
    return embed

class NameCharacter(discord.ui.Modal, title="Character Creation"):
    sel1 = discord.ui.TextInput(label='Name your character', placeholder="Your adventure starts here", max_length=15)
    def __init__(self, Selection):
        self.sele = Selection
        super().__init__(title="Character Creation")

    async def on_submit(self, interaction: Interaction):
        ClassStats = StartingClasses.get(self.sele)
        print(ClassStats)
        # Adds the character to the database following the information they have associated with their class
        cur.execute("INSERT INTO characters (ID, Name, Class, CurrentHP, BaseDPS, Weapon, Level, Xp, XPCap, CriticalChance, Inventory) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (interaction.user.id, str(self.sel1), self.sele, ClassStats[1], ClassStats[3], None, ClassStats[5], ClassStats[6], ClassStats[7], ClassStats[8], None))
        conn.commit()
        # Uses charcheck to get their character data just inserted to the db
        PlayerObject = AssignPlayer(interaction.user.id)
        #Player Object grabs the information from the db and passes it into the data structure Player object
        # Adds the embed to show player.
        embed = HomeEmbed(PlayerObject)
        # Add to db what worlds they have unlocked
        await interaction.response.edit_message(view=StartingMenu(interaction=interaction, player=PlayerObject), content=f'Welcome, {str(self.sel1)}, your adventure awaits. Please begin your adventure below.', embed=embed)



class MyButton(discord.ui.Button):
    async def callback(self, interaction:discord.Interaction,):
        await interaction.response.send_modal(NameCharacter(self.label))
   
class ClassSelection(InteractionCheck):
    def __init__(self, interaction:discord.Interaction):
        # The class that allows the player to choose their class, uses the Starting Class dictionary to automatically populate the classes field. TODO Use a db to change starting classes and associate them with abilities
        self.msg:discord.Interaction = interaction
        self.temp = self.msg
        super().__init__(self.msg)
        async def Selection(response):
            await interaction.followup.send(response)
        for i in StartingClasses.values():
            r = MyButton(label=i[0], custom_id=i[0])
            self.add_item(r)



def GenerateMobs(Char:Player):
    # TODO Generate mobs difficulty depending on player level Caps to a certain world. EX: If world 1 cap the mob level to a certain amount when comparing to player level
    c = 0
    cap = random.randint(1,3)
    mob = [] # Empty mob list to append data later
    while c < cap:
        c += 1
        mob.append(random.choice(list((mobs.values())))) # Append only mob object to list TODO use copy() if issues persist with unique game
    mob[:] = [copy(x) for x in mob] # Creates copies of each mob so they are not associated with the same mob in memory
    return mob

async def InitializeGame(msg:discord.Interaction, player:Player):
    print("Generating random enemies")
    mob = GenerateMobs(player) # Generates enemies based on parameters for the world
    embed = discord.Embed(title=f"{player.name}",description=f"Health: {player.current_hp}/{player.max_hp}")
    for i in mob:
        embed.add_field(name=f"{i.name}",value=f"{i.hp}/{i.max_hp}")
    await msg.response.edit_message(embed=embed, view=inGame(msg, embed, player, Game(player, mob, embed)))




class StartingMenu(InteractionCheck):
    def __init__(self, interaction, player):
        self.msg:discord.Interaction = interaction
        self.temp = self.msg
        self.player = player
        super().__init__(self.msg)

    
    @discord.ui.button(label="Initalize Game", style=discord.ButtonStyle.green)
    async def StartGame(self, inter: discord.Interaction, Empty):
        print(self.player)
        await InitializeGame(inter, self.player)


    @discord.ui.button(label="Stats", style=discord.ButtonStyle.blurple, emoji='📊')
    # TODO Get stats from the database and show it here, including critial chance and weapon damage.
    async def Stats(self, inter:discord.Interaction, Empty):
        embed = discord.Embed(title="Test",description=GenStats(inter.user.id))
        #embed.add_field(name="Foo",value="Bar")
        await inter.response.edit_message(content='',embed=embed)

    @discord.ui.button(label="Select World", style=discord.ButtonStyle.green, emoji='🌎')
    async def World(self, inter:discord.Interaction, Empty):
        pass

    @discord.ui.button(label=" Inventory",  style=discord.ButtonStyle.gray, emoji="💼",row=1)
    # TODO Have an inventory system
    async def Inventory(self, int: discord.Interaction, Empty):
        pass

    @discord.ui.button(label="Shop",  style=discord.ButtonStyle.gray, emoji="🪙",row=1)
    # TODO Add a variable shop with changing items per interval
    async def Shop(self, int: discord.Interaction, Empty):
        pass

class inGame(InteractionCheck):
    # The game instance, everything associated with the game is contained here and is per instance.
    def __init__(self, interaction, embed, player1, game:Game):
        self.msg:discord.Interaction = interaction
        self.embed = embed
        self.game = game
        self.player = player1
        super().__init__(self.msg)

    @discord.ui.button(label="Attack",  style=discord.ButtonStyle.green, emoji="⚔️")
    async def attack(self, inter: discord.Interaction, Empty:discord.ui.Button):
        await inter.response.defer()
        c = 0-1
        Empty.disabled = True
        select = discord.ui.Select()
        select.placeholder = "Which mob would you like to attack?"


        for i in self.game.moblist:
            c+=1
            if self.game.moblist[c].hp > 0:
                if len([x for x in self.game.moblist if AliveCheck(x)]) > 1: # Generates a list of mobs and checks the len for the alive mobs
                    select.add_option(label=f"{i.name}",description=f"{i.hp}/{i.max_hp}",value=c)
                    print(select.options)
                    select.max_values = 2
                    view = discord.ui.View()
                    view.add_item(select)

                    async def selcallback(inter2):
                        Result = await self.game.attack(inter2, self.player, [int(x) for x in select.values])
                        print(Result)

                        if Result == True:
                            await inter.followup.edit_message(message_id=inter.message.id,content="You have fallen in your last battle. How would you like to proceed?",view=StartingMenu(self.msg, AssignPlayer(inter.user.id)),embed=HomeEmbed(self.player))
                            #message_id=inter.message.id
                            return
                        
                        view.stop()
                    select.callback = selcallback
                else:
                    await self.game.attack(inter, self.player, [c])
                    Empty.disabled = False
                    view = self
                if len([x for x in self.game.moblist if AliveCheck(x)]) == 0:
                            # Pass in item rewards and generate items/drops if necessary as well as reward XP for each mob
                    await inter.followup.edit_message(message_id=inter.message.id,content="You have won your last battle. How would you like to proceed?",view=StartingMenu(self.msg, AssignPlayer(inter.user.id)),embed=HomeEmbed(self.player))
                    return
        

        await inter.followup.edit_message(message_id=inter.message.id, view=view)
        await view.wait()
        Empty.disabled = False
        await inter.message.edit(view=self)

    @discord.ui.button(label="Flee",  style=discord.ButtonStyle.red, emoji="🏃‍♂️")
    async def flee(self, int: discord.Interaction, Empty):
        await self.game.flee()

    @discord.ui.button(label=" Inventory",  style=discord.ButtonStyle.gray, emoji="💼")
    # TODO Inventory system in battle will only show usable items in battle and each item has an effect associated with db
    async def inventory(self, int: discord.Interaction, Empty):
        pass

@tree.command(name= 'start', description= "Test")
async def self(interaction: discord.Interaction):
    print(CharCheck(interaction.user.id))
    if CharCheck(interaction.user.id) == None:
        embed = discord.Embed(title="You do not yet have a character, please select a character class.",description="Each class has different starting stats, and abilties")
        for i in StartingClasses.values():
            embed.add_field(name=i[0],value=f"Stats: \nHealth: {i[1]}\nDamage: {i[3]}" ) #TODO Add abiltiies and crit chance to stats as well
        await interaction.response.send_message(embed=embed, view=ClassSelection(interaction))
        #for i in None:
        #    embed.add_field(name="Empty")
    else:
        game = copy(StartingMenu(interaction, AssignPlayer(interaction.user.id)))
        await interaction.response.send_message(content="Press play to start",view=game)

    #game = copy(StartingMenu(interaction))
    #await interaction.response.send_message(content="Press play to start",view=game)



client.run('')