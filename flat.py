import re
import resource
from defstat import *

class ClassListResource(resource.Resource):
    """ Represents a list of all Squeak classes. """

    def __init__(self, sn):
        resource.Resource.__init__(self, sn)

    def getattr(self):
        nlink = self.sn.getNumberOfClasses() + 2
        return DirStat(nlink)

    def readdir(self, offset):
        return self.sn.getAllClasses()

class FlatPathParser(resource.Parser):
    """ Converts a path into a resource. """

    root_exp = '^/((?P<class>(%s))(/((?P<file>(%s))|((?P<dir>(%s))(/(?P<method>(%s)))?)))?)?$' \
            % (resource.Parser.cls, resource.Parser.file, resource.Parser.dir, resource.Parser.method)
    path_exp = re.compile(root_exp)

    def __init__(self, sn):
        self.sn = sn

    def parse(self, path):
        try:
            res = self.path_exp.match(path).groupdict()
        except AttributeError:
            return resource.IllegalResource()

        if res['method']:
            if res['dir'] == 'instance':
                return resource.InstanceMethodResource(self.sn, res['class'], res['method'])
            elif res['dir'] == 'class':
                return resource.ClassMethodResource(self.sn, res['class'], res['method'])
        elif res['dir']:
            if res['dir'] == 'instance':
                return resource.InstanceMethodsDirectoryResource(self.sn, res['class'])
            if res['dir'] == 'class':
                return resource.ClassMethodsDirectoryResource(self.sn, res['class'])
            if res['dir'] == 'traits':
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
            return resource.ClassDirectoryResource(self.sn, res['class'])
        else:
            return ClassListResource(self.sn)
