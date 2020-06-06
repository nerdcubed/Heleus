import discord
import os
from discord.ext import commands
from utils import checks, yaml
from .fancyhelp import FancyHelp

class Help(commands.Cog):
    """Custom help messages WITH FANCY EMBEDS OOOOOO!"""
    def __init__(self, heleus):
        self.heleus = heleus
        self.group = os.environ.get('HELEUS_HELP_GROUP', 'cog')
        template = yaml.get_safe('help')
        self.heleus.help_command = FancyHelp(name=heleus.name, template=template, show_hidden=True)

    async def on_unload(self):
        self.heleus.help_command = discord.ext.commands.HelpCommand
