import fuse
import squeakNet
import logging
import re
#import cProfile
import resource
import hierarchy
import flat
import category
#import hotshot
#import hotshot.stats

from defstat import *

from fuse import Fuse

fuse.fuse_python_api = (0, 2)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='error.log',
                    filemode='a')

class RootDirectoryResource(resource.StaticDirectoryResource):
    contents = ['flat', 'hierarchy', 'category']

class PathParser:
    # Used to determine the fs and the subpath within that fs.
    path_exp = re.compile('/((?P<fs>\w+)(?P<subpath>/.+)?)?')

    # Used to determine if a path is a trait request.
    trait_exp = re.compile('/traits(?P<trait>/.+)')

    # Used to determine if a trait request is valid.
    # Doesn't re have a not operator? If so, this can be imbedded in
    # trait_exp.
    trait_false_exp = re.compile('/(instance|class|subclasses)/traits/')

    def __init__(self, sn):
        self.flat = flat.FlatPathParser(sn)
        self.hierarchy = hierarchy.HierarchyPathParser(sn)
        self.category = category.CategoryPathParser(sn)

    def trait(self, path):
        print path
        # Check if a trait request may be inappropriate
        if self.trait_false_exp.search(path) is not None:
            return None

        # Okay, attempt to extract the trait.
        res = self.trait_exp.search(path)
        if res is None:
            return None
        else:
            # Make sure we get the last trait entry.
            while res is not None:
                oldres = res
                res = self.trait_exp.search(res.groupdict()['trait'])
            print oldres.groupdict()['trait']
            return self.flat.parse(oldres.groupdict()['trait'])

    def parse(self, path):
        # First, check if this is a trait.
        res = self.trait(path)
        if res is not None:
            return res

        # Otherwise find the appropriate 
        d = self.path_exp.match(path).groupdict()
        if d['fs']:
            if not d['subpath']:
                d['subpath'] = '/'
            if d['fs'] == 'flat':
                return self.flat.parse(d['subpath'])
            elif d['fs'] == 'hierarchy':
                return self.hierarchy.parse(d['subpath'])
            elif d['fs'] == 'category':
                return self.category.parse(d['subpath'])
            else:
                return resource.IllegalResource()
        else:
            return RootDirectoryResource()
        
class SqueakFS(Fuse):
    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        #Let's try and get a connection to the squeak image
        logging.info("Initialized SqueakFS")

    def initializeConnection(self,port):
        self.sn = squeakNet.SqueakNet(port)
        self.parser = PathParser(self.sn)
        
    def getattr(self, path):
        """ Gets the attributes of a filesystem entry.

        Arguments:
            path    a path of the type /mnt/fisk representing the filesystem entry. 
            
        Returns:
                    a fuse.Stat object containing appropriate information for this
                    entry.

        """ 

        logging.debug("getattr %s" % path) 

        return self.parser.parse(path).getattr()

    def readdir(self, path, offset):
        """ Gets the contents of a filesystem directory. 
        
        This method is called whenever a query is made to list entries in a
        filesystem directory. An example of this is the unix application 'ls', which
        will list all entries in a directory. This method is expected to produce a
        list of all entries located at the specified path in the filesystem. If
        the query is invalid, for example if path represents an invalid filesystem
        entry, the method should return one of the error messages described in the
        errno module.

        Arguments:
            path    a path of the type /mnt/fisk representing the filesystem entry.
            offset  ignored.

        Returns:
                    a generator, whose elements are either a negative errno entry
                    or strings representing the names of entries in the specified
                    directory.

        """
        
        logging.debug("readdir %s, %s" % (path, offset))

        out = self.parser.parse(path).readdir(offset)
        for a in out:
            # TODO Discard all '/' and *, they break the filesystem!
            if '/' not in a and '*' not in a and not '\\' in a:            
                yield fuse.Direntry(a)

    def open(self, path, flags):
        logging.debug("open %s, %s" % (path, flags))
        
        return self.parser.parse(path).open(flags)

    def read(self, path, size, offset):
        logging.debug("read %s, %s %s" % (path, size, offset))

        return self.parser.parse(path).read(size, offset)
        
	
def main():
    usage="""
Squeak .image filesystem.
""" + Fuse.fusage

    server = SqueakFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')
    #This is the UGLIEST
    #piece of hack i've done in a long time
    #Can someone explain how command line arguments work for fuse? (in a not so ugly way?) 
    #Let me know jbjoerk@gmail.com

    server.squeakport = 40000
    server.parser.add_option(mountopt="squeakport",default="40000",
    help="The port the squeak server is running on.[default: %default]")
    
    server.parse(values=server,errex=1)
    server.initializeConnection(server.squeakport)
    
#    prof = hotshot.Profile("out.prof")
#    prof.runcall(server.main)
#    prof.close()
    server.main()
    
if __name__ == '__main__':
    main()
