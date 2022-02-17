import copy
import re
from collections import OrderedDict

import discord
from discord.ext import commands

from utils import checks


class FancyHelp(commands.HelpCommand):
    def __init__(self, **options):
        self.name = options.pop('name', 'Bot')
        template = options.pop('template', None)
        self.group_by = options.pop('group_by', 'cog')
        if template:
            self.template = self.construct_template(template)
        else:
            self.template = None
        self.regex = re.compile(r'(^.*)\n(^-+)', re.MULTILINE)

        super().__init__(**options)

    HIDDEN = '🕵️‍'
    # Used to help align text outside of code blocks
    TAB = '   '
    # Used for when we need an embed field value to
    # be blank for whatever reason. Discord doesn't
    # like TAB for this.
    BLANK = 'ᅟᅟᅟᅟᅟᅟᅟᅟ'

    async def can_run(self, cmd):
        if self.verify_checks:
            try:
                return await cmd.can_run(self.context)
            except commands.CommandError:
                return False
        else:
            return True

    def get_colour(self):
        if not self.context.guild:
            return discord.Colour.blurple()
        colour = self.context.guild.me.colour
        return colour

    def split_description(self, description):
        groups = [
            x
            for x in self.regex.findall(description)
            if len(x[0]) == len(x[1])
        ]
        if not groups:
            return description, None
        topics = []
        final_desc = None
        prev = None
        for title, split in groups:
            combined = f'{title}\n{split}'
            sections = description.split(combined)
            if not final_desc:
                final_desc = sections.pop(0).strip()
            elif prev:
                topics.append((prev, sections.pop(0).strip()))
            for x in sections[:-1]:
                topics.append((prev, x))
            description = sections[-1]
            prev = title
        topics.append((prev, description))
        return final_desc, topics

    def construct_template(self, template):
        if 'title' not in template:
            template['title'] = f'❓ {self.name} Help'
        if 'color' not in template:
            template['colour'] = None
        if 'description' not in template:
            template['description'] = self.context.bot.description

        return discord.Embed().from_dict(template)

    def get_ending_note(self, command=None):
        if not command:
            return f'Use {self.clean_prefix}{self.invoked_with} [command] for more info on a command.'
        if isinstance(command, commands.Group):
            return (
                f'To use a subcommand, use {self.clean_prefix}{command.qualified_name} [command].\n'
                f'Use {self.clean_prefix}{self.invoked_with} {command.qualified_name} [command] '
                'for more info on a subcommand.'
            )
        else:
            return None

    def get_command_signature(self, command):
        return (
            f'{self.clean_prefix}{command.qualified_name}'
            f'{" " + command.signature if command.signature else ""}'
        )

    def generate_command_strs(self, _commands):
        max_length = 0
        is_owner = checks.owner_check(self.context)
        for command in _commands:
            if not command.hidden or is_owner:
                length = len(command.name)
                if command.hidden:
                    length += 2
                if length > max_length:
                    max_length = length
        command_list = []
        for command in _commands:
            if not command.hidden or is_owner:
                string = f'`{command.name}`'
                if command.hidden:
                    string += self.HIDDEN
                    add = -1
                else:
                    add = 1
                for i in range(0, max_length - len(command.name) + add):
                    string += self.TAB
                string += command.short_doc
                # Let's set a somewhat reasonable limit
                if len(string) > 512:
                    string = string[:509] + '...'
                command_list.append(string)
        return command_list

    def format_commands(self, formatted_commands: dict, embed=None):
        embeds = []
        char_limit = 0
        if embed:
            embed = copy.deepcopy(embed)
            embeds.append(embed)
            char_limit += (
                len(embed.title)
                + len(embed.description)
                + len(embed.footer.text)
                + len(embed.author.name)
                + sum([len(x.name) + len(x.value) for x in embed.fields])
            )
            colour = embed.colour
        else:
            colour = self.get_colour()
            embed = discord.Embed(colour=colour)

        for field_name, _commands in formatted_commands.items():
            write_desc = False
            string = ''
            char_limit += len(field_name)
            for command in _commands:
                # Grant a little overhead just in case
                if (
                    char_limit + len(command) >= 5500
                    or len(embed.fields) == 24
                ):
                    embeds.append(embed)
                    embed = discord.Embed(colour=colour)
                    char_limit = 8
                    string = ''
                    field_name = self.BLANK
                    write_desc = True
                if len(string) + len(command) + 1 <= (
                    2048 if write_desc else 1024
                ):
                    to_add = command if not string else f'\n{command}'
                    char_limit += len(to_add)
                    string += to_add
                else:
                    if write_desc:
                        embed.description = string
                    embed.add_field(
                        name=field_name, value=string, inline=False
                    )
                    string = ''
                    field_name = self.BLANK
                    char_limit += 8
            embed.add_field(name=field_name, value=string, inline=False)

        if embed not in embeds:
            embeds.append(embed)

        return embeds

    async def send_bot_help(self, mapping):
        if self.template:
            embed = self.template
            if not embed.colour:
                embed.colour = self.get_colour()
        else:
            embed = discord.Embed(colour=self.get_colour())
            embed.title = f'❓ {self.name} Help'
            embed.description = self.context.bot.description

        desc_format = OrderedDict()
        if self.group_by == 'cog':
            for cog, _commands in mapping.items():
                name = 'No Category' if cog is None else cog.qualified_name
                filtered = await self.filter_commands(_commands, sort=True)
                if filtered:
                    formatted = self.generate_command_strs(filtered)
                    desc_format[name] = formatted
        else:
            groups = {}
            for cog, _commands in mapping.items():
                filtered = await self.filter_commands(_commands, sort=True)
                if filtered:
                    if hasattr(cog, 'help_group'):
                        groups.setdefault(cog.help_group, []).extend(filtered)
                    elif not cog:
                        for command in filtered:
                            if hasattr(command, 'help_group'):
                                groups.setdefault(
                                    command.help_group, []
                                ).append(command)
                            else:
                                groups.setdefault('No Category', []).append(
                                    command
                                )
                    else:
                        groups.setdefault('No Category', []).extend(filtered)
            groups = OrderedDict(sorted(groups.items()))
            for group, _commands in groups.items():
                _commands.sort(key=lambda x: x.qualified_name)
                formatted = self.generate_command_strs(_commands)
                desc_format[group] = formatted

        if desc_format:
            embeds = self.format_commands(desc_format, embed)
            embeds[-1].set_footer(text=self.get_ending_note())
            for e in embeds:
                await self.get_destination().send(embed=e)
        else:
            await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(colour=self.get_colour())
        embed.set_author(name='❓ Cog Help')
        embed.description = f'**{cog.qualified_name}**'
        if hasattr(cog, 'help_image'):
            embed.set_thumbnail(url=cog.help_image)
        if cog.description:
            description, topics = self.split_description(cog.description)
            embed.description += f'\n\n{description}'
            if topics:
                for topic, text in topics:
                    embed.add_field(
                        name=topic,
                        value=text if text else self.BLANK,
                        inline=False,
                    )

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        if filtered:
            formatted = self.generate_command_strs(filtered)
            embeds = self.format_commands({'Commands': formatted}, embed)
            embeds[-1].set_footer(text=self.get_ending_note())
            for e in embeds:
                await self.get_destination().send(embed=e)
        elif checks.owner_check(self.context):
            # Only reveal details about an empty cog to the bot owner
            embed.set_footer(text=self.get_ending_note())
            await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        if not await self.can_run(group):
            return
        embed = discord.Embed(colour=self.get_colour())
        embed.set_author(name='❓ Command Help')
        if group.cog:
            embed.description = (
                f'**{group.cog.qualified_name} • {group.qualified_name}**'
            )
            if hasattr(group, 'help_image'):
                embed.set_thumbnail(url=group.help_image)
            elif hasattr(group.cog, 'help_image'):
                embed.set_thumbnail(url=group.cog.help_image)
        else:
            if hasattr(group, 'help_image'):
                embed.set_thumbnail(url=group.help_image)
            embed.description = f'**{group.qualified_name}**'

        embed.add_field(
            name='Usage',
            value=f'`{self.get_command_signature(group)}`',
            inline=False,
        )

        if group.help:
            description, topics = self.split_description(group.help)
            embed.add_field(
                name='Description', value=description, inline=False
            )
            if topics:
                for topic, text in topics:
                    embed.add_field(
                        name=topic,
                        value=text if text else self.BLANK,
                        inline=False,
                    )

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            if filtered:
                formatted = self.generate_command_strs(filtered)
                embeds = self.format_commands(
                    {'Subcommands': formatted}, embed
                )
                embeds[-1].set_footer(text=self.get_ending_note(group))
                for e in embeds:
                    await self.get_destination().send(embed=e)
            else:
                embed.set_footer(text=self.get_ending_note())
                await self.get_destination().send(embed=embed)
        else:
            embed.set_footer(text=self.get_ending_note())
            await self.get_destination().send(embed=embed)

    send_command_help = send_group_help
