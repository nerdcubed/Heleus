from .core import Core

def setup(heleus):
    heleus.add_cog(Core(heleus))
