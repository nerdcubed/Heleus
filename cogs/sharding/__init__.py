from .sharding import Sharding


def setup(heleus):
    if heleus.shard_id is not None:
        heleus.add_cog(Sharding(heleus))
    else:
        raise RuntimeError('this cog requires your bot to be sharded')
