from .help import Help


def setup(heleus):
    help_cog = Help(heleus)
    heleus.add_cog(help_cog)
    heleus.help_command.cog = help_cog
