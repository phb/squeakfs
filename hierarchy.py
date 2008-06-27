import os.path
import re
import fuse
import logging
import errno
import resource
import traceback
from defstat import *
from squeakNet import SqueakNetException

class HierarchyClassDirectoryResource(resource.StaticDirectoryResource):
    """ Represents the base directory of a class as used by SqueakFS. """

    contents = ['superclass', 'instancemembers', 'classmembers', 'comment', 'instance', 'class', 'subclasses', 'traits']

    def __init__(self, sn, cls):
        resource.StaticDirectoryResource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.NOENT
        return resource.StaticDirectoryResource.getattr(self)

class ClassRootResource(resource.StaticDirectoryResource):
    """ Represents the top most root of the inheritence tree. """

    contents = ['ProtoObject']

class SubClassesDirectoryResource(resource.Resource):
    """ Represents a list of subclasses of a class. """

    def __init__(self, sn, cls):
        resource.Resource.__init__(self, sn)
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassAvailable(self.cls):
            return -errno.ENOENT
        nlink = len(self.sn.getDirectSubClasses(self.cls)) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getDirectSubClasses(self.cls)

class HierarchyPathParser(resource.Parser):
    """ Creates a request from a path. """

    # Regular expressions used for matching.
    dir = resource.Parser.dir + '|subclasses'
    path = '^(?P<prefix>(/(\w+)/subclasses)*)(?P<suffix>/(%s(/((%s)|((%s)(/%s)?)))?)?)$' \
            % (resource.Parser.cls, resource.Parser.file, dir, resource.Parser.method)
    path_exp = re.compile(path)
    prefix_exp = re.compile('/(\w+)/subclasses')
    suffix_exp = re.compile('^/((?P<class>%s)(/((?P<file>%s)|(?P<dir>%s)(/(?P<method>(%s)))?))?)?$' \
            % (resource.Parser.cls, resource.Parser.file, dir, resource.Parser.method))

    def __init__(self, sn):
        self.sn = sn

    def validate(self, cls, hierarchy):
        # Check that the first class in the hierarchy is the ProtoObject.
        if hierarchy and hierarchy[0] != 'ProtoObject':
            return False

        # Check that all following classes descend from the one before it.
        for i in range(1, len(hierarchy)):
            superclass = self.sn.getSuperClass(hierarchy[i])
            if superclass != hierarchy[i-1]:
                return False

        # Finally, check that cls is a descendant of the last class in the hierarchy.
        if cls:
            try:
                superclass = self.sn.getSuperClass(cls)
            except SqueakNetException:
                logging.debug(traceback.format_exc())
                return False

            if cls != 'ProtoObject' and superclass != hierarchy[-1]:
                return False

        return True

    def parse(self, path):
        try:
            req = self.path_exp.match(path).groupdict()
            res = self.suffix_exp.search(req['suffix']).groupdict()
        except AttributeError:
            return resource.IllegalResource()

        self.prefix_exp.findall(req['prefix'])
        hierarchy = [x.group(1) for x in self.prefix_exp.finditer(req['prefix'])]
        if not self.validate(res['class'], hierarchy):
            return resource.IllegalResource()

        if res['method']:
            if res['dir'] == 'instance':
                return resource.InstanceMethodResource(self.sn, res['class'], res['method'])
            elif res['dir'] == 'class':
                return resource.ClassMethodResource(self.sn, res['class'], res['method'])
        elif res['dir']:
            if res['dir'] == 'instance':
                return resource.InstanceMethodsDirectoryResource(self.sn, res['class'])
            elif res['dir'] == 'class':
                return resource.ClassMethodsDirectoryResource(self.sn, res['class'])
            elif res['dir'] == 'subclasses':
                return SubClassesDirectoryResource(self.sn, res['class'])
            elif res['dir'] == 'traits':
                return resource.TraitsDirectoryResource(self.sn, res['class'])
        elif res['file']:
            if res['file'] == 'classmembers':
                return resource.ClassMembersResource(self.sn, res['class'])
            elif res['file'] == 'instancemembers':
                return resource.InstanceMembersResource(self.sn, res['class'])
            elif res['file'] == 'superclass':
                return resource.SuperClassResource(self.sn, res['class'])
            elif res['file'] == 'comment':
                return resource.ClassCommentResource(self.sn, res['class'])
        elif res['class']:
            return HierarchyClassDirectoryResource(self.sn, res['class'])
        else:
            return ClassRootResource(self.sn)
