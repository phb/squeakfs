import logging
import errno
import traceback

from defstat import *
from squeakNet import SqueakNetException

""" Defines some common resources.

A resource is a piece of data in the filesystem on which all the normal
filesystem operations may be performed. There may, for example, be different
types of files on a filesystem and performing getattr, open, read etc may
mean different things for different types of files. Using resources means
allowing each of of these types to be defined by itself.

Resources can be created by a resource factory that can take some sort of 
input, a path for example, and decide on what type of resource this input
represents.

"""

class Resource:
    """ A basic SqueakFS resource.

    Resource objects represent some squeak resource. They may be queried using
    filesystem operations. Subclasses of Resource will typically override 
    appropriate methods of this class to perform checks and fetch data.

    """

    def __init__(self, sn=None):
        """ Creates a new Resource.
        
        Optionally, a resource may be initialized with a SqueakNet object
        which will be made available to the methods of the class. Subclasses
        of Resource are encouraged to accept other data appropriate for the
        type of resource.

        """

        self.sn = sn

    def getattr(self):
        """ Get filesystem attributes for this resource.

        This method is called anytime a resource is used. It should return a
        stat object or a negative errno error if some sort of error has
        occurred.

        Note: Because getattr is always called when an operation is invoked on
        this resource, you may make validity checks on the object here and 
        choose to not do so for the other methods of this class. 
        
        """

        raise NotYetImplemented

    def readdir(self, offset):
        """ Get the contents of a directory.

        This method will only be called if someone has identified this resource
        to be a directory. The method should return a list containing all the 
        entries in the directory.

        """

        raise NotYetImplemented
    
    def open(self, flags):
        """ Check if this resource may be opened for file operations.

        This method will only be called if someone has identified this resource
        to be a file. The method need not return anything special. However, if an 
        error occurred it should return a negative errno error.

        """

        raise NotYetImplemented

    def read(self, size, offset):
        """ Read a chunk of data from this resource.

        This method will only be called if someone has identified this resource
        to be a file. The method should return a string containing up to size
        characters.

        """

        raise NotYetImplemented

class FileResource(Resource):
    """ A resource representing a file. """

    def extract(self, data, size, offset):
        """ Extracts a segment of data.

        The segment will be extracted at the given offset and up to size characters
        will be extracted.

        """

        slen = len(data)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = data[offset:offset+size]
        else:
            buf = ''
        return buf

class StaticDirectoryResource(Resource):
    """ A directory resource with constant content.
    
    Subclasses of this class need only override content if a list containing the
    directory entries.
    
    """
    
    content = None

    def getattr(self):
        nlink = len(self.contents) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.contents

class IllegalResource(Resource):
    """ A resource that doesn't exist.

    This resource may be used if one before hand knows that a requested resource
    doesn't exist. Whenever an operation is performed on it it will return an
    error.

    """

    def getattr(self):
        return -errno.ENOENT

    def readdir(self, offset):
        return -errno.ENOENT

    def open(self, flags):
        return -errno.ENOENT

    def read(self, size, offset):
        return -errno.ENOENT

class ClassCommentResource(FileResource):
    """ Represents the comment entry of a Squeak class. """

    def __init__(self, sn, cls):
        FileResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        try:
            size = len(self.sn.getClassComment(self.cls))
        except SqueakNetException, e:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = self.sn.getClassComment(self.cls)
        return self.extract(s, size, offset)

class SuperClassResource(FileResource):
    """ Represents the superclass entry of a Squeak class. """
    
    def __init__(self, sn, cls):
        FileResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        try:
            size = len(self.sn.getSuperClass(self.cls)) + 1
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = self.sn.getSuperClass(self.cls) + '\n'
        return self.extract(s, size, offset)

class InstanceMethodResource(FileResource):
    """ Represents an instance method of a Squeak class. """

    def __init__(self, sn, cls, method):
        FileResource.__init__(self, sn)
        self.cls = cls
        self.method = method

    def getattr(self):
        try:
            size = len(self.sn.getInstanceMethod(self.cls, self.method))
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = self.sn.getInstanceMethod(self.cls, self.method)
        return self.extract(s, size, offset)

class ClassMethodResource(FileResource):
    """ Represents a class method of a Squeak class. """

    def __init__(self, sn, cls, method):
        FileResource.__init__(self, sn)
        self.cls = cls
        self.method = method

    def getattr(self):
        try:
            size = len(self.sn.getClassMethod(self.cls, self.method))
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = self.sn.getClassMethod(self.cls, self.method)
        return self.extract(s, size, offset)

class InstanceMembersResource(FileResource):
    """ Represents a list of instance members of a Squeak class. """

    def __init__(self, sn, cls):
        FileResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        try:
            members = self.sn.getInstanceMembers(self.cls)
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        size = sum([len(x) for x in members]) + len(members)
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = '\n'.join(self.sn.getInstanceMembers(self.cls)) + '\n'
        return self.extract(s, size, offset)

class ClassMembersResource(FileResource):
    """ Represents a list of class members of a squeak class. """

    def __init__(self, sn, cls):
        FileResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        try:
            members = self.sn.getClassMembers(self.cls)
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        size = sum([len(x) for x in members]) + len(members)
        return FileStat(size)

    def open(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, size, offset):
        s = '\n'.join(self.sn.getClassMembers(self.cls)) + '\n'
        return self.extract(s, size, offset)

class ClassDirectoryResource(StaticDirectoryResource):
    """ Represents the base directory of a Squeak class as used by SqueakFS. """

    contents = ['superclass', 'instancemembers', 'classmembers', 'comment', 'instance', 'class', 'traits']

    def __init__(self, sn, cls):
        StaticDirectoryResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.ENOENT
        return StaticDirectoryResource.getattr(self)

class ClassMethodsDirectoryResource(Resource):
    """ Represents a list of class methods for a Squeak class. """

    def __init__(self, sn, cls):
        Resource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.ENOENT
        nlink = len(self.sn.getClassMethodsInClass(self.cls)) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getClassMethodsInClass(self.cls)

class InstanceMethodsDirectoryResource(Resource):
    """ Represents a list of instance methods for a Squeak class. """
    def __init__(self, sn, cls):
        Resource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.ENOENT
        nlink = len(self.sn.getInstanceMethodsInClass(self.cls)) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getInstanceMethodsInClass(self.cls)

class TraitsDirectoryResource(Resource):
    """ Represents a list of traits for a Squeak class. """
    def __init__(self, sn, cls):
        Resource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.ENOENT
        nlink = len(self.sn.getTraits(self.cls)) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getTraits(self.cls)

class Parser:
    special_chars = '\-+~<=>@&\|&=!,\'().:'
    cls = '\w+'
    file = 'comment|classmembers|instancemembers|superclass'
    dir = 'instance|class|traits'
    method = '[\w%s]+' % special_chars
