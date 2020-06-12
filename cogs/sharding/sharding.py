import platform

import datetime
from discord.ext import commands

from utils import checks
from utils.runtime import CoreMode

try:
    import tabulate
    import psutil
except ImportError:
    raise RuntimeError('tabulate and psutil are required for this cog')


tabulate.MIN_PADDING = 0  # makes for a neater table


def gather_info(heleus):
    return {'status': heleus.settings[heleus.instance_id]['mode'].value, 'guilds': len(heleus.guilds),
            'members': len(set(heleus.get_all_members())), 'up_since': heleus.boot_time,
            'messages_seen': heleus.get_cog('Sharding').messages, 'host': platform.node().lower(),
            'memory': psutil.Process().memory_full_info().uss / 1024**2,
            'host_uptime': psutil.boot_time()}


def set_mode(heleus, mode):
    heleus.settings[heleus.instance_id]['mode'] = mode
    heleus.settings.commit(heleus.instance_id)


def _halt(heleus, ignore=None):
    if heleus.shard_id == ignore:
        return
    heleus.loop.create_task(heleus.get_cog('Core').halt_())


class Sharding(commands.Cog):
    def __init__(self, heleus):
        self.heleus = heleus
        self.lines = []
        self.messages = 0
        self.help_group = 'Core'
        self.help_image = 'https://i.imgur.com/RQmzK6i.png'

    @commands.Cog.listener()
    async def on_message(self, _):
        self.messages += 1

    @commands.group(invoke_without_command=True)
    async def shards(self, ctx):
        """A bunch of sharding-related commands."""
        await self.heleus.send_command_help(ctx)

    @shards.command()
    async def list(self, ctx, mode='generic'):
        """Lists all shards.

        * mode: "generic" or "host"

        Arguments marked with * are optional.
        """
        if mode.lower() not in ('generic', 'host'):
            await ctx.send('Invalid mode.')
            return await self.heleus.send_command_help(ctx)
        msg = await ctx.send('Fetching statistics, please wait...')
        shards = await self.heleus.run_on_shard('all', gather_info)
        for shard, resp in dict(shards).items():
            print(shard, resp)
            if repr(resp) == '<NoResponse>':
                shards[shard] = {'status': CoreMode.down.value}

        table = []
        if mode == 'generic':
            table = [['Active', 'Shard', 'Status', 'Guilds', 'Members', 'Messages', ]]
            for shard, state in shards.items():
                line = ['*' if shard == self.heleus.shard_id else '', shard+1, state['status'],
                        state.get('guilds', ''),
                        state.get('members', ''),
                        state.get('messages_seen', '')]
                table.append(line)
        if mode == 'host':
            table = [['Active', 'Shard', 'Status', 'Host', 'Memory', 'Up Since', 'Host Up Since']]
            for shard, state in shards.items():
                line = ['*' if shard - 1 == self.heleus.shard_id else '', shard, state['status'],
                        state.get('host', ''),
                        state.get('memory', ''),
                        datetime.datetime.utcfromtimestamp(state.get('up_since', 0)) if state.get('up_since') else '',
                        datetime.datetime.utcfromtimestamp(state.get('host_uptime', 0)) if state.get('host_uptime')
                        else '']
                table.append(line)
        table = f'```prolog\n{tabulate.tabulate(table, tablefmt="psql", headers="firstrow")}\n```'
        await msg.edit(content=table)

    @shards.command()
    async def get(self, ctx):
        """Gets the current shard."""
        await ctx.send(f'I am shard {self.heleus.shard_id+1} of {self.heleus.shard_count}.')

    @shards.command()
    @checks.is_owner()
    async def set_mode(self, ctx, shard: int, mode: CoreMode):
        """Sets a shard's mode.

        - shard: The shard of which you want to set the mode
        - mode: The mode you want to set the shard to
        """
        active = await self.heleus.ping_shard(shard-1)
        if not active:
            return await ctx.send('Shard not online.')
        if self.heleus.shard_id == shard-1 and mode in (CoreMode.down, CoreMode.boot):
            return await ctx.send('This action would be too dangerous to perform on the current shard. Try running '
                                  'this command from a different shard targeting this one.')
        await self.heleus.run_on_shard(shard-1, set_mode, mode)
        await ctx.send('Mode set.')

    @shards.command(aliases=['shutdown'])
    @checks.is_owner()
    async def halt(self, ctx, shard: int):
        """Halts a shard.

        - shard: The shard you want to halt
        """
        active = await self.heleus.ping_shard(shard-1)
        if not active:
            return await ctx.send('Shard not online.')
        await self.heleus.run_on_shard(shard-1, _halt)
        await ctx.send('Halt command sent.')

    @shards.command()
    @checks.is_owner()
    async def halt_all(self, ctx):
        """Halts all shards."""
        msg = await ctx.send('Sending command...')
        await self.heleus.run_on_shard('all', _halt, self.heleus.shard_id)
        await msg.edit(content='Thank you for using Heleus.')
        await self.heleus.get_cog('Core').halt_()
