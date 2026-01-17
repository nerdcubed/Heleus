import logging

from disnake import abc
from disnake.ext import commands


class CommandLog(commands.Cog):
    """A simple cog to log commands executed."""

    def __init__(self):
        self.log = logging.getLogger("heleus.command_log")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        kwargs = ", ".join([f"{k}={repr(v)}" for k, v in ctx.kwargs.items()])
        args = f"with arguments {kwargs} " if kwargs else ""
        if ctx.guild:
            msg = (
                f'{ctx.author} ({ctx.author.id}) executed command "{ctx.command}" {args}in {ctx.guild} '
                f"({ctx.guild.id})"
            )
        elif isinstance(ctx.channel, abc.PrivateChannel):
            msg = f'{ctx.author} ({ctx.author.id}) executed command "{ctx.command}" {args}in DMs'
        else:
            msg = f'{ctx.author} ({ctx.author.id}) executed command "{ctx.command}" {args}in a guild'
        if ctx.bot.shard_id is not None:
            msg += f" on shard {ctx.bot.shard_id + 1}"
        self.log.info(msg)
