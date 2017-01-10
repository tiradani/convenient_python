import sys

def _under_24():
    if sys.version_info[0] < 2: return True
    if sys.version_info[0] == 2:
        return sys.version_info[1] < 4
    return False

def _under_26():
    if sys.version_info[0] < 2: return True
    if sys.version_info[0] == 2:
        return sys.version_info[1] < 6
    return False
