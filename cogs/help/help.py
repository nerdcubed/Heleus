import discord
import os
from discord.ext import commands
from utils import checks

class FancyHelp(commands.HelpCommand):
    COLOUR = discord.Colour.blurple()
    HIDDEN = "🕵️‍"

    def get_ending_note(self, command = None):
        if not command:
            return f'Use {self.clean_prefix}{self.invoked_with} [command] for more info on a command.'
        if isinstance(command, commands.Group):
            return (
                f'To use a subcommand, use {self.clean_prefix}{command.qualified_name} [command].\n'
                f'Use {self.clean_prefix}{self.invoked_with} {command.qualified_name} [command] for more info on a subcommand.'
            )
        else:
            return None

    def get_command_signature(self, command):
        return (
            f'{self.clean_prefix}{command.qualified_name}'
            f'{" "+ command.signature if command.signature else ""}'
            )
    
    def generate_command_strs(self, commands):
        max_length = 0
        is_owner = checks.owner_check(self.context)
        for command in commands:
            if not command.hidden or is_owner:
                length = len(command.name)
                if command.hidden:
                    length += 2
                if length > max_length:
                    max_length = length
        command_list = []
        for command in commands:
            if not command.hidden or is_owner:
                string = f'`{command.name}`'
                if command.hidden:
                    string += self.HIDDEN
                    add = -1
                else:
                    add = 1
                for i in range(0, max_length - len(command.name) + add):
                    string += '   '
                string += command.short_doc
                # Let's set a somewhat reasonable limit
                if len(string) > 512:
                    string = string[:509] + '...'
                command_list.append(string)
        return command_list
    
    def format_commands(self, formatted_commands:dict, embed = None):
        embeds = []
        char_limit = 0
        if embed:
            embeds.append(embed)
            char_limit += len(embed.title) + len(embed.description) + len(embed.footer.text) \
                + len(embed.author.name) + sum([len(x.name) + len(x.value) for x in embed.fields])
        else:
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
                    field_name = '   '
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
                    field_name = '   '
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
        embeds[0].title = '❓ Bot Help'
        description = self.context.bot.description
        if description:
            embeds[0].description = description

        embeds[-1].set_footer(text=self.get_ending_note())
        for embed in embeds:
            await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(colour=self.COLOUR)
        embed.set_author(name='❓ Cog Help')
        embed.description = f'**{cog.qualified_name}**'
        if cog.description:
            embed.description += f'\n\n{cog.description}'
        
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        if filtered:
            formatted = self.generate_command_strs(filtered)
            embeds = self.format_commands({'Commands': formatted}, embed)
            embeds[-1].set_footer(text=self.get_ending_note())
            for e in embeds:
                await self.get_destination().send(embed=e)
        else:
            embed.set_footer(text=self.get_ending_note())
            await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(colour=self.COLOUR)
        embed.set_author(name='❓ Command Help')
        if group.cog:
            embed.description = f'**{group.cog.qualified_name} • {group.qualified_name}**'
        else:
            embed.description = f'**{group.qualified_name}**'
        
        embed.add_field(name='Usage', value=f'`{self.get_command_signature(group)}`', inline=False)

        if group.help:
            embed.add_field(name='Description', value=group.help, inline=False)

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            if filtered:
                formatted = self.generate_command_strs(filtered)
                embeds = self.format_commands({'Subcommands': formatted}, embed)
            embeds[-1].set_footer(text=self.get_ending_note(group))
            for e in embeds:
                await self.get_destination().send(embed=e)
        else:
            embed.set_footer(text=self.get_ending_note())
            await self.get_destination().send(embed=embed)
        

    send_command_help = send_group_help


class Help(commands.Cog):
    """Custom help messages WITH FANCY EMBEDS OOOOOO!"""
    def __init__(self, heleus):
        self.heleus = heleus
        self.group = os.environ.get('HELEUS_HELP_GROUP', 'cog')
        self.heleus.help_command = FancyHelp(show_hidden=True)
