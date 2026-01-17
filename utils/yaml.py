import errno
import logging
import os

import strictyaml

logger = logging.getLogger("heleus")

folder = os.environ.get("HELEUS_CONFIG", "config")


def get(file: str, schema: strictyaml.Map = None):
    path = f"{folder}/{file}"
    if not os.path.exists(path):
        path += ".yml"
    if not os.path.exists(path):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), f"{folder}/{file}"
        )
    with open(path, "r") as f:
        return strictyaml.load(f.read(), schema).data


def get_safe(file: str, schema: strictyaml.Map = None):
    try:
        return get(file, schema)
    except FileNotFoundError:
        return None
    except Exception:
        logger.exception(f"Failed to parse help file: {file}")
        return None
