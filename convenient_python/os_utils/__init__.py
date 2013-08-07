import os
import sys
import errno
import pwd
import socket
import shutil
import grp  # @UnresolvedImport
import stat
import time
import glob
import fnmatch

class FileOperationError(Exception): pass
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

def mkdir_p(path):
    """
    Mimics the shell command "mkdir -p" in that it will attempt to create any
    missing directories in the specified path.

    @type path: C{str}
    @param path: directories specified by path to be created

    @raise FileOperationError: Any OS error that occurs during ownersip change
    """
    try:
        os.makedirs(path)
    except OSError, ose:
        if ose.errno == errno.EEXIST:
            pass
        else:
            error_message = "Error creating path (%s):\n%s" % (path, str(ose))
            raise FileOperationError(error_message)

def chmod(mode, path, recurse=False):
    """
    Change file or directory permissions.

    @type mode: C{oct}
    @param mode: New permissions for file or directory

    @type path: C{str}
    @param path: path whose permissions are about to be changed

    @type recurse: C{bool}
    @param recurse: Recurse through all files and sub directories if path is a
    directory and this variable == True.

    @raise FileOperationError: Any OS error that occurs during ownersip change
    """
    try:
        if recurse:
            for root, dirs, files in os.walk(path):
                for directory in dirs:
                    os.chmod(os.path.join(root, directory), mode)
                for filename in files:
                    os.chmod(os.path.join(root, filename), mode)
        else:
            os.chmod(path, mode)
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message = "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n %s" % exc_value
        else:
            error_message = "unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def chown(uid, gid, path, recurse=False):
    """
    Change owner of file or directory.

    @type uid: C{int}
    @param uid: UID of new owner

    @type gid: C{int}
    @param gid: GID of new owner

    @type path: C{str}
    @param path: path whose ownership is about to be changed

    @type recurse: C{bool}
    @param recurse: Recurse through all files and sub directories if path is a
    directory and this variable == True.

    @raise FileOperationError: Any OS error that occurs during ownersip change
    """
    try:
        if recurse:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for directory in dirs:
                        os.chown(os.path.join(root, directory), uid, gid)
                    for filename in files:
                        os.chown(os.path.join(root, filename), uid, gid)
            else:
                error_message = "Recurse has been specified and Path (%s) is " \
                                "not a directory."
                raise FileOperationError(error_message)
        else:
            os.chown(path, uid, gid)
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message = "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n%s" % exc_value
        else:
            error_message = "unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def get_host():
    """
    Returns host information.

    @rtype: C{tuple}
    @param: A tuple containing the host name, the ip address, and the fully
    qualified domain name.
    """
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    fqdn = socket.getfqdn()

    return (hostname, ip_addr, fqdn)

def cd(path):
    """
    Change to directory specified by path

    @type path: C{str}
    @param path: file to be removed

    @type recurse: C{bool}
    @param recurse: if true, the function will delete all files and  
    sub-directories as well

    @raise FileOperationError: Any OS error that occurs during directory change
    """
    try:
        os.chdir(path)
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        error_message = "Failed to change directory.\n\n"

        if ose.errno == errno.EPERM:
            error_message += "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message += "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message += "Permission denied:\n%s" % exc_value
        else:
            error_message += "Unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def rm(path, recurse=False):
    """
    Remove file or directory specified by path
    
    @type path: C{str}
    @param path: file to be removed

    @type recurse: C{bool}
    @param recurse: if true, the function will delete all files and  
    sub-directories as well

    @raise FileOperationError: Any OS error that occurs during path removal
    """
    if os.path.isdir(path):
        try:
            if recurse:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        except shutil.Error:
            _, exc_value, _ = sys.exc_info()
            error_message = "Error removing %s:\n%s" % (path, exc_value)
            raise FileOperationError(error_message)
        except OSError, ose:
            _, exc_value, _ = sys.exc_info()
            error_message = "Failed to remove %s.\n\n" % path

            if ose.errno == errno.EPERM:
                error_message += "Operation not permitted:\n%s" % exc_value
            elif ose.errno == errno.ENOENT:
                error_message += "No such file or directory:\n%s" % exc_value
            elif ose.errno == errno.EACCES:
                error_message += "Permission denied:\n%s" % exc_value
            else:
                error_message += "Unknown error occurred:\n%s" % exc_value
            raise FileOperationError(error_message)
    elif os.path.isfile(path) or os.path.islink(path):
        try:
            os.remove(path)
        except OSError, ose:
            _, exc_value, _ = sys.exc_info()
            error_message = "Failed to remove %s.\n\n" % path

            if ose.errno == errno.EPERM:
                error_message += "Operation not permitted:\n%s" % exc_value
            elif ose.errno == errno.ENOENT:
                error_message += "No such file or directory:\n%s" % exc_value
            elif ose.errno == errno.EACCES:
                error_message += "Permission denied:\n%s" % exc_value
            else:
                error_message += "Unknown error occurred:\n%s" % exc_value
            raise FileOperationError(error_message)
    else:
        error_message = "Failed to remove %s. No such file or directory." % path
        raise FileOperationError(error_message)

def cp(source, destination):
    """
    Copy a path to a new path

    @type source: C{str}
    @param source: source path to be copied, supports wildcards

    @type dest_path: C{str}
    @param dest_path: Destination path that the source will be copied to.

    @raise FileOperationError: Any OS error that occurs during copy
    """
    try:
        sources = glob.glob(source)
        try:
            os.path.exists(sources[0])
        except IndexError:
            raise FileOperationError("No file matching %s" % str(source))

        for item in sources:
            shutil.copy2(item, os.path.join(destination, os.path.basename(item)))

    except shutil.Error:
        _, exc_value, _ = sys.exc_info()
        error_message = "Error copying %s to %s:\n%s" % (source, destination, exc_value)
        raise FileOperationError(error_message)

def mv(source, destination, overwrite=False):
    """
    Attempts to move a path to a new path
    
    @type source: C{str}
    @param source: The path that will be moved, supports wildcards

    @type destination: C{str}
    @param destination: The destination path

    @type overwrite_new: C{bool}
    @param overwrite_new: Whether to overwite the destination or not

    @raise FileOperationError: Any OS error that occurs during path move
    """

    if os.path.exists(destination) and not overwrite:
        raise FileOperationError("Destination path already exists")

    try:
        sources = glob.glob(source)
        try:
            os.path.exists(sources[0])
        except IndexError:
            raise FileOperationError("No file matching %s" % str(source))

        for item in sources:
            shutil.move(item, os.path.join(destination, os.path.basename(item)))

    except shutil.Error:
        _, exc_value, _ = sys.exc_info()
        error_message = "Error moving %s to %s:\n%s" % (source, destination,
                                                        exc_value)
        raise FileOperationError(error_message)


def safe_write(path, file_data):
    """
    check if path exists, if yes move original to new name write path
    
    NOTE: the backup name is not guaranteed to be unique if you perform multiple
    writes in less than a second

    NOTE: this does *NOT* append

    @type path: C{str}
    @param path: The path to write the data to

    @type file_data: C{str}
    @param file_data: The data to write into the file specified by path

    @raise FileOperationError: Any OS error that occurs during file backup or
    writing to the new file.
    """

    try:
        if os.path.exists(path):
            directory = os.path.dirname(path)
            filename = os.path.basename(path)
            extension = str(time.time())
            backup_name = "%s/%s.bck_%s" % (directory, filename, extension)
            shutil.copy2(path, backup_name)

        fd = open(path, 'w')
        fd.write(file_data)
        fd.close()
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message = "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n%s" % exc_value
        else:
            error_message = "Unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def ls(directory):
    """
    Convenience function for os.listdir; returns a directory listing.

    Returns a list of the directory contents filtered for files only.  
    Optionally, the list can sorted by a specified key function.
    
    @type directory: C{str}
    @param directory: The directory which will be listed.

    @rtype: C{list}
    @param: A list containing the directory listing.

    @raise FileOperationError: Any OS error that occurs during directory 
    lookup.
    """
    try:
        return os.listdir(directory)
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message = "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n%s" % exc_value
        else:
            error_message = "Unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def ls_files(directory, sort=False, reverse=False, key=str.lower):
    """
    Returns a list of the directory contents filtered for files only.  
    Optionally, the list can sorted by a specified key function.
    
    @type directory: C{str}
    @param directory: The directory which will be listed.

    @type sort: C{bool}
    @param sort: Should we sort the file list?

    @type reverse: C{bool}
    @param reverse: Direction of the sort.  Only has effect if sort == True

    @type key: C{func}
    @param key: Function to use for comparing list objects.  Defaults to case
    insensitive string sort.

    @rtype: C{list}
    @param: A list of the files in the directory, optionally sorted.

    @raise FileOperationError: Any OS error that occurs directory lookup.
    """

    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(f)]
        if sort:
            files.sort(key=key, reverse=reverse)
        return files
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.ENOENT:
            error_message = "No such file or directory:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n%s" % exc_value
        else:
            error_message = "Unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

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

def touch(path, mode=0600):
    """
    Mimics the shell "touch" command in that it creates a zero length file with
    the specified mode.

    @type path: C{str}
    @param path: The name for which to search.

    @type mode: C{oct}
    @param mode: Arguments to L{os.access}.

    @raise FileOperationError: Any OS error that occurs
    """
    try:
        os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, mode), 'w').close()
    except OSError, ose:
        _, exc_value, _ = sys.exc_info()
        if ose.errno == errno.EPERM:
            error_message = "Operation not permitted:\n%s" % exc_value
        elif ose.errno == errno.EACCES:
            error_message = "Permission denied:\n%s" % exc_value
        else:
            error_message = "Unknown error occurred:\n%s" % exc_value
        raise FileOperationError(error_message)

def which(name, flags=os.X_OK):
    """
    Search PATH for executable files with the given name. Code adapted from:

    http://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/twisted/python/procutils.py

    @type name: C{str}
    @param name: The name for which to search.

    @type flags: C{int}
    @param flags: Arguments to L{os.access}.

    @rtype: C{list}
    @param: A list of the full paths to files found, in the order in which they
    were found.
    """
    result = []
    path = os.environ.get('PATH', None)
    if path is None: return []

    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
    return result

def _is_dir_excluded(directory, exclude_dirs):
    should_be_excluded = False
    if isinstance(exclude_dirs, list):
        for ex_dir in exclude_dirs:
            if ex_dir in directory:
                should_be_excluded = True
                break
    elif isinstance(exclude_dirs, str):
        if exclude_dirs in directory:
            should_be_excluded = True

    return should_be_excluded

def find_files(directory, pattern, exclude_dirs=None):
    for root, _, files in os.walk(directory):
        # check to see if any exclude directories passed in match
        if _is_dir_excluded(root, exclude_dirs): continue
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename
