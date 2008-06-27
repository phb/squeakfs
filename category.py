import re
import resource
import errno
import traceback
import logging
from defstat import *
from squeakNet import SqueakNetException

class CategoryClassCommentResource(resource.ClassCommentResource):
    def __init__(self, sn, category, cls):
        resource.ClassCommentResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.ClassCommentResource.getattr(self)

class CategorySuperClassResource(resource.SuperClassResource):
    def __init__(self, sn, category, cls):
        resource.SuperClassResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.SuperClassResource.getattr(self)

class CategoryClassMembersResource(resource.ClassMembersResource):
    def __init__(self, sn, category, cls):
        resource.ClassMembersResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.ClassMembersResource.getattr(self)

class CategoryInstanceMembersResource(resource.InstanceMembersResource):
    def __init__(self, sn, category, cls):
        resource.InstanceMembersResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.InstanceMembersResource.getattr(self)

class CategoryClassMethodResource(resource.ClassMethodResource):
    def __init__(self, sn, category, cls, protocol, method):
        resource.ClassMethodResource.__init__(self, sn, cls, method)
        self.category = category
        self.protocol = protocol

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        if self.protocol != '--all--' and not self.sn.isClassMethodInProtocol(self.method, self.protocol, self.cls):
            return -errno.ENOENT
        return resource.ClassMethodResource.getattr(self)

class CategoryInstanceMethodResource(resource.InstanceMethodResource):
    def __init__(self, sn, category, cls, protocol, method):
        resource.InstanceMethodResource.__init__(self, sn, cls, method)
        self.category = category
        self.protocol = protocol

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        if self.protocol != '--all--' and not self.sn.isInstanceMethodInProtocol(self.method, self.protocol, self.cls):
            return -errno.ENOENT
        return resource.InstanceMethodResource.getattr(self)

class CategoryClassProtocolResource(resource.Resource):
    def __init__(self, sn, category, cls, protocol):
        resource.Resource.__init__(self, sn)
        self.category = category
        self.cls = cls
        self.protocol = protocol

    def getattr(self):
        if not self.sn.isClassProtocolAvailable(self.protocol, self.cls):
            return -errno.ENOENT
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        try:
            nlink = len(self.sn.getMethodsInClassProtocol(self.cls, self.protocol)) + 2
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getMethodsInClassProtocol(self.cls, self.protocol)

class CategoryInstanceProtocolResource(resource.Resource):
    def __init__(self, sn, category, cls, protocol):
        resource.Resource.__init__(self, sn)
        self.category = category
        self.cls = cls
        self.protocol = protocol

    def getattr(self):
        if not self.sn.isInstanceProtocolAvailable(self.protocol, self.cls):
            return -errno.ENOENT
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        try:
            nlink = len(self.sn.getMethodsInInstanceProtocol(self.cls, self.protocol)) + 2
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getMethodsInInstanceProtocol(self.cls, self.protocol)

class CategoryInstanceAllProtocolsResource(resource.InstanceMethodsDirectoryResource):
    def __init__(self, sn, category, cls):
        resource.InstanceMethodsDirectoryResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.InstanceMethodsDirectoryResource.getattr(self)

class CategoryClassAllProtocolsResource(resource.ClassMethodsDirectoryResource):
    def __init__(self, sn, category, cls):
        resource.ClassMethodsDirectoryResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.ClassMethodsDirectoryResource.getattr(self)

class CategoryInstanceProtocolListResource(resource.Resource):
    def __init__(self, sn, category, cls):
        resource.Resource.__init__(self, sn)
        self.category = category
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        try:
            nlink = len(self.sn.getInstanceProtocols(self.cls)) + 3
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getInstanceProtocols(self.cls) + ['--all--']

class CategoryClassProtocolListResource(resource.Resource):
    def __init__(self, sn, category, cls):
        resource.Resource.__init__(self, sn)
        self.category = category
        self.cls = cls

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        try:
            nlink = len(self.sn.getClassProtocols(self.cls)) + 3
        except SqueakNetException:
            logging.debug(traceback.format_exc())
            return -errno.ENOENT
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getClassProtocols(self.cls) + ['--all--']

class CategoryClassDirectoryResource(resource.ClassDirectoryResource):

    def __init__(self, sn, category, cls):
        resource.ClassDirectoryResource.__init__(self, sn, cls)
        self.category = category

    def getattr(self):
        if not self.sn.isClassInCategory(self.category, self.cls):
            return -errno.ENOENT
        return resource.ClassDirectoryResource.getattr(self)

class CategoryResource(resource.Resource):
    def __init__(self, sn, category):
        resource.Resource.__init__(self, sn)
        self.category = category

    def getattr(self):
        if not self.sn.isCategoryAvailable(self.category):
            return -errno.ENOENT
        nlink = len(self.sn.getClassesInCategory(self.category)) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getClassesInCategory(self.category)

class CategoryListResource(resource.Resource):
    def getattr(self):
        nlink = len(self.sn.getCategories()) + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getCategories()

class CategoryPathParser(resource.Parser):
    """ Converts a path into a resource. """

    category = '[\w\s-]+'
    protocol = '[\w\s%s]+' % resource.Parser.special_chars

    path_exp = re.compile('^/((?P<category>(%s))(/(?P<class>(%s))(/((?P<file>(%s))|((?P<dir>(%s))(/(?P<protocol>(%s))(/(?P<method>(%s)))?)?)))?)?)?$' \
            % (category, resource.Parser.cls, resource.Parser.file, resource.Parser.dir, protocol, resource.Parser.method))

    def __init__(self, sn):
        self.sn = sn

    def match(self, path):
        return self.path_exp.match(path).groupdict()

    def parse(self, path):
        try:
            res = self.match(path)
        except AttributeError:
            return resource.IllegalResource()

        if res['method']:
            return self.method(res)
        elif res['protocol']:
            return self.protocol(res)
        elif res['dir']:
            return self.dir(res)
        elif res['file']:
            return self.file(res)
        elif res['class']:
            return self.cls(res)
        elif res['category']:
            return self.category(res)
        else:
            return CategoryListResource(self.sn)

    def category(self, res):
        return CategoryResource(self.sn, res['category'])

    def file(self, res):
        if res['file'] == 'superclass':
            return CategorySuperClassResource(self.sn, res['category'], res['class'])
        if res['file'] == 'comment':
            return CategoryClassCommentResource(self.sn, res['category'], res['class'])
        if res['file'] == 'classmembers':
            return CategoryClassMembersResource(self.sn, res['category'], res['class'])
        if res['file'] == 'instancemembers':
            return CategoryInstanceMembersResource(self.sn, res['category'], res['class'])

    def method(self, res):
        if res['dir'] == 'instance':
            return CategoryInstanceMethodResource(self.sn, res['category'], res['class'], res['protocol'], res['method'])
        elif res['dir'] == 'class':
            return CategoryClassMethodResource(self.sn, res['category'], res['class'], res['protocol'], res['method'])

    def protocol(self, res):
        if res['protocol'] == '--all--':
            if res['dir'] == 'instance':
                return CategoryInstanceAllProtocolsResource(self.sn, res['category'], res['class'])
            elif res['dir'] == 'class':
                return CategoryClassAllProtocolsResource(self.sn, res['category'], res['class'])
        else:
            if res['dir'] == 'instance':
                return CategoryInstanceProtocolResource(self.sn, res['category'], res['class'], res['protocol'])
            elif res['dir'] == 'class':
                return CategoryClassProtocolResource(self.sn, res['category'], res['class'], res['protocol'])

    def dir(self, res):
        if res['dir'] == 'instance':
            return CategoryInstanceProtocolListResource(self.sn, res['category'], res['class'])
        elif res['dir'] == 'class':
            return CategoryClassProtocolListResource(self.sn, res['category'], res['class'])
        elif res['dir'] == 'traits':
            return resource.TraitsDirectoryResource(self.sn, res['class'])

    def cls(self, res):
        return CategoryClassDirectoryResource(self.sn, res['category'], res['class'])
