from .sharding import Sharding

def setup(liara):
    if liara.shard_id is not None:
        liara.add_cog(Sharding(liara))
    else:
        raise RuntimeError('this cog requires your bot to be sharded')
