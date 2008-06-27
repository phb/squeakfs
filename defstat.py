import fuse
import os
import stat

""" Contains stat entries for use with squeakfs. """

class DefaultStat(fuse.Stat):
    """ A stat class with all values set to 0.
    
    - st_mode (protection bits)
    - st_ino (inode number)
    - st_dev (device)
    - st_nlink (number of hard links)
    - st_uid (user ID of owner)
    - st_gid (group ID of owner)
    - st_size (size of file, in bytes)
    - st_atime (time of most recent access)
    - st_mtime (time of most recent content modification)
    - st_ctime (platform dependent; time of most recent metadata change on Unix,
                    or the time of creation on Windows).
    
    """

    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = os.getuid()   # Use the users uid.
        self.st_gid = os.getgid()   # Use the users gid.
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class FileStat(DefaultStat):
    """ A stat entry for a typical file. """

    def __init__(self, size):
        DefaultStat.__init__(self)
        self.st_mode = stat.S_IFREG | 0644
        self.st_nlink = 2
        self.st_size = size

class DirStat(DefaultStat):
    """ A stat entry for a typical directory. """
    def __init__(self, nlink):
        DefaultStat.__init__(self)
        self.st_mode = stat.S_IFDIR | 0755
        self.st_nlink = nlink
