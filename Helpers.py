import os
import hashlib
import base64


# get a root directory
def get_root_path():
    return os.path.dirname(os.path.realpath(__file__))


def is_base64(str):
    try:
        return base64.b64encode(base64.b64decode(str)) == str
    except Exception:
        return False
