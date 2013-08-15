import os
import sys
import pwd
import grp  # @UnresolvedImport
import stat

class UidGidError(Exception): pass

def drop_privileges(username):
    """
    Drop privileges from root to a non-privileged user.

    NOTE: Must be running as root to drop privileges.

    @type username: C{str}
    @param username: Unprivileged user that we are are going to run as.
    """
    # check if we are root.  If we are, drop privileges
    start_uid = os.getuid()
    if start_uid == 0:
        # NOTE:  Must set gid first or you will get an 
        #        "Operation not permitted" error
        pwd_tuple = pwd.getpwnam(username)
        pw_uid = pwd_tuple[2]
        pw_gid = pwd_tuple[3]

        os.setregid(pw_gid, pw_gid)
        os.setreuid(pw_uid, pw_uid)
    else:
        # Not root so we can't change privileges so pass
        pass

def getuid(username):
    """
    Retrieves the uid from /etc/passwd for the specified user name.

    @type username: C{str}
    @param username: The name for which to search.

    @raise UidGidError: Any error that occurs during user lookup
    """
    try:
        return pwd.getpwnam(username)[2]
    except:
        _, exc_value, _ = sys.exc_info()
        error_message = "Unknown error occurred:\n%s" % exc_value
        raise UidGidError(error_message)

def getgid(groupname):
    """
    Retrieves the gid from /etc/group for the specified group name.

    @type groupname: C{str}
    @param groupname: The name for which to search.

    @raise UidGidError: Any error that occurs during group lookup
    """
    try:
        return grp.getgrnam(groupname)[2]
    except:
        _, exc_value, _ = sys.exc_info()
        error_message = "Unknown error occurred:\n%s" % exc_value
        raise UidGidError(error_message)

def has_permissions(path, level, perms):
    """
    Checks the path for the specified permissions at the specified level.

    Example:  Check ~/.bashrc for user execute permisions
            has_permissions("~/.bashrc", "USR", "X")

    NOTE: does not follow symbolic links

    @type path: C{str}
    @param path: The path for which to check permisions.

    @type level: C{str}
    @param level: The level of permission - User, Group, or Other.  Valid values
        are one of the following: USR, GRP, OTH

    @type perms: C{str}
    @param perms: String containing the permissions to check for - Read, Write,
    Execute.  This string can be any combination of the following letters:
    R, W, X.
    """
    result = True
    try:
        mode = stat.S_IMODE(os.lstat(path)[stat.ST_MODE])
        for perm in perms:
            if mode & getattr(stat, "S_I" + perm + level):
                continue
            result = False
            break
    except:
        result = False

    return result

