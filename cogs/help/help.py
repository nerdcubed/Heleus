import discord
import os
from discord.ext import commands
from utils import checks
from .fancyhelp import FancyHelp

class Help(commands.Cog):
    """Custom help messages WITH FANCY EMBEDS OOOOOO!"""
    def __init__(self, heleus):
        self.heleus = heleus
        self.group = os.environ.get('HELEUS_HELP_GROUP', 'cog')
        self.heleus.help_command = FancyHelp(show_hidden=True)
