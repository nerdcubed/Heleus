import disnake as discord
import os
from disnake.ext import commands
from utils import checks, yaml
from .fancyhelp import FancyHelp


class Help(commands.Cog):
    """Custom help messages WITH FANCY EMBEDS OOOOOO!"""

    def __init__(self, heleus):
        self.heleus = heleus
        self.group_type = os.environ.get('HELEUS_HELP_GROUP', 'cog')
        template = yaml.get_safe('help')
        self.heleus.help_command = FancyHelp(
            name=heleus.name,
            template=template,
            group_by=self.group_type,
            show_hidden=True,
        )
        self.help_group = 'General'
        self.help_image = 'https://i.imgur.com/AZWeMcH.png'

    async def on_unload(self):
        self.heleus.help_command = discord.ext.commands.HelpCommand
