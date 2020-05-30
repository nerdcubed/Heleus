import logging
from discord.ext import commands


class CommandLog(commands.Cog):
    """A simple cog to log commands executed."""
    def __init__(self):
        self.log = logging.getLogger('heleus.command_log')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        kwargs = ', '.join([f'{k}={repr(v)}' for k, v in ctx.kwargs.items()])
        args = f'with arguments {kwargs} ' if kwargs else ''
        msg = f'{ctx.author} ({ctx.author.id}) executed command "{ctx.command}" {args}in {ctx.guild} ({ctx.guild.id})'
        if ctx.bot.shard_id is not None:
            msg += f' on shard {ctx.bot.shard_id+1}'
        self.log.info(msg)
