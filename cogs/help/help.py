import discord
import os
from discord.ext import commands
from utils import checks

class FancyHelp(commands.HelpCommand):
    COLOUR = discord.Colour.blurple()
    HIDDEN = "\\🕵️‍"

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(self.clean_prefix, self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)
    
    def generate_command_strs(self, commands):
        max_length = 0
        is_owner = checks.owner_check(self.context)
        for command in commands:
            if not command.hidden or is_owner:
                length = len(command.name)
                if length > max_length:
                    max_length = length
        command_list = []
        for command in commands:
            if not command.hidden or is_owner:
                string = f'`{command.name}`'
                if command.hidden:
                    string += self.HIDDEN
                for i in range(0, max_length - len(command.name) + 1):
                    string += '   '
                string += command.short_doc
                # Let's set a somewhat reasonable limit
                if len(string) > 512:
                    string = string[:509] + '...'
                command_list.append(string)
        return command_list
    
    def format_commands(self, formatted_commands:dict):
        embeds = []
        char_limit = 0

        embed = discord.Embed(colour=self.COLOUR)
        
        for field_name, commands in formatted_commands.items():
            write_desc = False
            string = ''
            char_limit += len(field_name)
            for command in commands:
                # Grant a little overhead just in case
                if char_limit + len(command) >= 5500 or len(embed.fields) == 24:
                    embeds.append(embed)
                    embed = discord.Embed(colour=self.COLOUR)
                    char_limit = 8
                    string = ''
                    field_name = 'ᅟᅟᅟᅟᅟᅟᅟᅟ'
                    write_desc = True
                if len(string) + len(command) + 1 <= (2048 if write_desc else 1024):
                    to_add = command if not string else f'\n{command}'
                    char_limit += len(to_add)
                    string += to_add
                else:
                    if write_desc:
                        embed.description = string
                    embed.add_field(name=field_name, value=string, inline=False)
                    string = ''
                    field_name = 'ᅟᅟᅟᅟᅟᅟᅟᅟ'
                    char_limit += 8
            embed.add_field(name=field_name, value=string, inline=False)
        
        if embed not in embeds:
            embeds.append(embed)
        
        return embeds

    async def send_bot_help(self, mapping):
        desc_format = {}
        for cog, commands in mapping.items():
            name = 'No Category' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                formatted = self.generate_command_strs(filtered)
                desc_format[name] = formatted
        if desc_format:
            embeds = self.format_commands(desc_format)
        else:
            embeds = [discord.Embed(colour=self.COLOUR)]
        embeds[0].title = 'Bot Commands'
        description = self.context.bot.description
        if description:
            embeds[0].description = description

        embeds[-1].set_footer(text=self.get_ending_note())
        for embed in embeds:
            await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog), colour=self.COLOUR)
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embeds = []
        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            if filtered:
                formatted = self.generate_command_strs(filtered)
                embeds = self.format_commands({'Subcommands': formatted})

        if not embeds:
            embeds = [discord.Embed(colour=self.COLOUR)]
        
        embeds[0].title = group.qualified_name

        if group.help:
            embeds[0].description = group.help

        embeds[-1].set_footer(text=self.get_ending_note())
        for embed in embeds:
            await self.get_destination().send(embed=embed)

    send_command_help = send_group_help


class Help(commands.Cog):
    """Custom help messages WITH FANCY EMBEDS OOOOOO!"""
    def __init__(self, heleus):
        self.heleus = heleus
        self.group = os.environ.get('HELEUS_HELP_GROUP', 'cog')
        self.heleus.help_command = FancyHelp()
