import re
import socket
import string
import errno

class SqueakNetException(Exception):
    """
    Exception class for SqueakNet errors
    """
    def __init__(self, errormessage,errnum):
        self.errmsg = errormessage
        self.errnum = errnum
    def __str__(self):
        return "SqueakNetException[%d]: %s\n" % (self.errnum,self.errmsg)

class SqueakNet():
    """
    A class to handle communication with the SqueakFS Squeak TCP Server.
    TODO: We need to magically support all of squeak's CR/CRLF/\t etc etc.
    """
    def __init__(self,port):
        self.host='localhost'
        self.port=int(port)
        self.timeouts = 0
        self.MAX_TIMEOUT = 5 #5 timeouts a`1 second before giving up.
        self.__connectSocket()
        
        self.replacevars = {'\\': "__BACKSLASH__",
                            '/': "__SLASH__",
                            '*': "__STAR__"}
        self.backwards_replacevars = {"__BACKSLASH__": '\\',
                            "__SLASH__": '/' ,
                            "__STAR__": '*' }
    
    def __connectSocket(self):
        if self.timeouts > self.MAX_TIMEOUT:
            #Okay, server is dead, let's give up.
            self.sock = None
            raise SqueakNetException("Socket not connected",-2)
            
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#        self.sock.settimeout(1)
        self.sock.connect((self.host,self.port))
#        self.sFile = self.sock.makefile("rw",2048)
        
    def sendConvertSpecial(self,str):
        self.send(re.sub(r'(__STAR__)|(__BACKSLASH__)|(__SLASH__)', lambda m: self.backwards_replacevars[m.group(0)],str))

    def send(self,str):
        if(not self.sock):
            raise SqueakNetException("Socket not connected",-2)
        try:
            self.__send(str)
        except socket.error, e:
            #Most probably a Broken Pipe, let's confirm
            if e[0] == errno.EPIPE:
                self.timeouts = self.timeouts + 1
                self.__connectSocket()
                self.send(str) #try again.
                return #raise SqueakNetException("Broken pipe",e[0])
            else:
                raise
        
    def __send(self,str):
        self.sock.send(str + "\n")
    
    def recv(self):
        return self.__recv()
            
    def __recv(self):
        if(not self.sock):
            raise SqueakNetException("Socket not connected",-2)
            
        try:
            #Receive data length 
#            recvlen = self.sFile.readline() #breaks on LF
#            recvlen = int(recvlen)
#            results = self.sFile.read(recvlen)
            data = self.sock.recv(1024)
            res = data.split("\n",1)
	    results = res[1]
            while(int(res[0]) != len(results)):
                results = results + self.sock.recv(int(res[0])-len(results))

            if(results.startswith("Error:")):
                raise SqueakNetException(results,-1)
        except socket.timeout,e:
            #Socket probably dead. Let's try and reconnect it.
            self.timeouts = self.timeouts + 1
            self.__connectSocket()
            raise SqueakNetException("Error: Timeout",-1)
        return results
    
    def readResponse(self):
        return self.__recv()
        
    def readResponseConvertNL(self):
        data = self.recv().replace("\r","\n") + "\n"
        return data
    
    def readResponseAsArray(self):
        data = self.__recv().rstrip("\r").split("\r")
        if(data[0] == ''): data = []
        return data

    def readResponseAsArrayConvertSpecial(self):
        data = self.__recv().rstrip("\r").split("\r")
        if(data[0] == ''): data = []        
        return map(lambda x: re.sub('[\\*\/]', lambda m: self.replacevars[m.group(0)],x),data)
        
    def readResponseAsBool(self):
        try:
            data = self.__recv()
        except SqueakNetException,e:
            return False
        return True
        
    def getSuperClass(self,inClass):
        """
        Receives the name of the superclass.
        """
        self.sendConvertSpecial("getSuperClass:\t%s"%(inClass))
        return self.readResponse()
    
    def getSubClasses(self,inClass):
        """
        Receives the names of all subclasses in an array.
        """
        self.sendConvertSpecial("getSubClasses:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()
    
    def getDirectSubClasses(self,inClass):
        """
        Receives the names of all direct subclasses in an array.
        """
        self.sendConvertSpecial("getDirectSubClasses:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()
                
    def getAllClasses(self):
        """
        Receives the name of all classes as an array.
        """
        self.send("getAllClasses")
        return self.readResponseAsArrayConvertSpecial()
        
    def getInstanceMethod(self,inClass,method):
        """
        Receives the sourcecode of an instancemethod. 
        XXX: How to output this in a good way? They use \r for newlines.
        """
        self.sendConvertSpecial("getInstanceMethod:InClass:\t%s\t%s"%(method,inClass))    
        return self.readResponseConvertNL()


    def getClassMethod(self,inClass,method):
        """
        Receives the sourcecode of a classmethod. 
        """
        
        self.sendConvertSpecial("getClassMethod:InClass:\t%s\t%s"%(method,inClass))    
        return self.readResponseConvertNL()
        
    def getCategories(self):
        """
        Receives a list with all top-level categories.
        """        
        self.send("getCategories")
        return self.readResponseAsArrayConvertSpecial()
    
    def getClassMembers(self,inClass):
        """
        Receives a list of all class member variables.
        """
        self.sendConvertSpecial("getClassMembers:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()        
        
    def getInstanceMembers(self,inClass):
        """
        Receives a list of all instance member variables.
        """
        self.sendConvertSpecial("getInstanceMembers:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()
    
    def getInstanceProtocols(self,inClass):
        """
        Receives a list of all protocols for instance methods.
        Note, this does not contain -- all --, as that one is just faked by the standard squeak browser.
        """
        self.sendConvertSpecial("getInstanceProtocols:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()

    def getClassProtocols(self,inClass):
        """
        Receives a list of all protocols for class methods.
        Note, this does not contain -- all --, as that one is just faked by the standard squeak browser.
        """
        self.sendConvertSpecial("getClassProtocols:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()


    def getMethodsInInstanceProtocol(self,inClass,inProtocol):
        """
        Receives all methods in an instanceprotocol.
        You can't use -- all -- here.
        """
        self.sendConvertSpecial("getMethodsInInstanceProtocol:InClass:\t%s\t%s"%(inProtocol,inClass))
        return self.readResponseAsArrayConvertSpecial()

    def getMethodsInClassProtocol(self,inClass,inProtocol):
        """
        Receives all methods in a classprotocol.
        You can't use -- all -- here.
        """
        self.sendConvertSpecial("getMethodsInClassProtocol:InClass:\t%s\t%s"%(inProtocol,inClass))
        return self.readResponseAsArrayConvertSpecial()

    
    def getClassComment(self,inClass):
        """
        Receives the comment of a class.
        """
        self.sendConvertSpecial("getClassComment:\t%s"%(inClass))
        return self.readResponseConvertNL()

    def getClassesInCategory(self,category):
        """
        Receives the classes available under a category.
        """
        self.sendConvertSpecial("getClassesInCategory:\t%s"%(category))
        return self.readResponseAsArrayConvertSpecial()  
        
    def getInstanceMethodsInClass(self,inClass):
        """
        Returns an array with all instancemethods in a class.
        """
        self.sendConvertSpecial("getInstanceMethodsInClass:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()
        
    def getClassMethodsInClass(self,inClass):
        """
        Returns an array with all classmethods in a class
        """
        self.sendConvertSpecial("getClassMethodsInClass:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()

    def getTraits(self,inClass):
        self.sendConvertSpecial("getTraits:\t%s"%(inClass))
        return self.readResponseAsArrayConvertSpecial()
    
    def getAllTraits(self):
        self.send("getAllTraits")
        return self.readResponseAsArrayConvertSpecial()

    def getTraitUsers(self,inTrait):
        self.sendConvertSpecial("getTraitUsers:\t%s"%(inTrait))
        return self.readResponseAsArrayConvertSpecial()
    def isTrait(self,inClass):
        self.sendConvertSpecial("isTrait:\t%s"%(inClass))
        return self.readResponseAsBool()

    def isClassAvailable(self,inClass):
        """
        Checks if a class is available in the squeak image. 
        returns True if it's available.
        """
        self.sendConvertSpecial("isClassAvailable:\t%s"%(inClass))
        return self.readResponseAsBool()

    def isInstanceMethodAvailable(self,inClass,method):
        """
        Checks if a instance method is available for the selected class.
        """
        self.sendConvertSpecial("isInstanceMethodAvailable:inClass:\t%s\t%s"%(method,inClass))        
        return self.readResponseAsBool()
                
    def isClassMethodAvailable(self,inClass,method):
        """
        Checks if an class method is available for the selected class
        FIXME: Make this faster.
        """        
        
        try:
            res = self.getClassMethod(inClass,method)
        except SqueakNetException,e:
            return False
        return True
    
    def isInstanceProtocolAvailable(self,protocol,inClass):
        """
        """
        self.sendConvertSpecial("isInstanceProtocolAvailable:inClass:\t%s\t%s"%(protocol,inClass))
        return self.readResponseAsBool()
    
    def isClassProtocolAvailable(self,protocol,inClass):
        self.sendConvertSpecial("isClassProtocolAvailable:inClass:\t%s\t%s"%(protocol,inClass))
        return self.readResponseAsBool()
        
    def isCategoryAvailable(self,category):    
        self.sendConvertSpecial("isCategoryAvailable:inClass:\t%s\t%s"%(category))
        return self.readResponseAsBool()
        
    def isClassMethodInProtocol(self,method,protocol,inClass):
        self.sendConvertSpecial("isClassMethod:InProtocol:inClass:\t%s\t%s\t%s"%(method,protocol,inClass))
        return self.readResponseAsBool()
        
    def isInstanceMethodInProtocol(self,method,protocol,inClass):
        self.sendConvertSpecial("isInstanceMethod:InProtocol:inClass:\t%s\t%s\t%s"%(method,protocol,inClass))
        return self.readResponseAsBool()

    def isClassInCategory(self,category,inClass):
        self.sendConvertSpecial("isClass:InCategory:\t%s\t%s"%(inClass,category))
        return self.readResponseAsBool()

    def isCategoryAvailable(self,category):
        self.sendConvertSpecial("isCategoryAvailable:\t%s"%(category))
        return self.readResponseAsBool()

    def getNumberOfClasses(self):
        self.send("getNumberOfClasses")
        return int(self.readResponse())
        
if __name__ == "__main__":
    print "Please run unittests (py.test) or squeakfs.py to start the filesystem"
    k = SqueakNet(40000)
    k.isInstanceMethodAvailable("Project","children")
    k.isClassMethodAvailable("Project","sdfs")
    
