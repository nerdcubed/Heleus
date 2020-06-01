import strictyaml
import os
import errno

folder = os.environ.get('HELEUS_CONFIG', 'config')

def get(file:str, schema:strictyaml.Map = None):
    path = f'{folder}/{file}'
    if not os.path.exists(path):
        path += '.yml'
    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f'{folder}/{file}')
    with open(path, 'r') as f:
        return strictyaml.load(f, schema)
