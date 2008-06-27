import unittest
import os
import py

import squeakNet

class TestSqueakNet():
    """
    Testclass to test the communication layer
    We also test that we receive correct data from the Squeak server.
    """
    
    def setup_method(self, method):
        self.sn = squeakNet.SqueakNet(40000)
        pass
        
    def teardown_method(self, method):
        pass
    
    def test_InvalidMessage(self):
        self.sn.send("SdshgsfgaASDFsd sdfs sdfs Tjopidiheeej")
        py.test.raises(squeakNet.SqueakNetException,self.sn.recv)
        #Let's send a 'almost' valid message but with a nonexistant class
        self.sn.send("getAllClasses and I have no clue what the heck I am doing!")
        py.test.raises(squeakNet.SqueakNetException,self.sn.recv)
                    
    def test_getSuperclass(self):
        res = self.sn.getSuperClass("Object")
        assert(res == "ProtoObject")

        res = self.sn.getSuperClass("SqueakFSNetwork")
        assert( res == "TcpService")
        
        py.test.raises(squeakNet.SqueakNetException,self.sn.getSuperClass,"asdfadfasdf sdfsdf ")
        

    def test_getSubClasses(self):
        res = self.sn.getSubClasses("TcpService")
        assert("SqueakFSNetwork" in res)
        py.test.raises(squeakNet.SqueakNetException,self.sn.getSubClasses,"TcpServicesdfsdfss")

        res = self.sn.getSubClasses("LargePositiveInteger")
        assert(len(res) == 1 and "LargeNegativeInteger" in res)
        #Extend test!!

    def test_getAllClasses(self):
        res = self.sn.getAllClasses()
        assert("SqueakFSNetwork" in res and "SqueakFS" in res and "Object" in res)
                    
    def test_getInstanceMethod(self):
        #TODO!: This test SUCKS
        res = self.sn.getInstanceMethod("SqueakFSNetwork","userActiongetInstanceMethod:InClass:")
        assert(len(res) > 10)

    def test_WeirdJapanseClassMethod(self):
        res = self.sn.getClassMethod("JapaneseEnvironment","flapTabTextFor:in:")
        #This used to crash our system as it returns data in a different encoding. 
        #It will raise exception and havoc if the bug isn't fixed.
        res = self.sn.getClassMethod("JapaneseEnvironment","flapTabTextFor:in:")
        
    def test_getClassMethod(self):
        res = self.sn.getClassMethod("Categorizer","allCategory")
        assert(len(res) > 10)

    def test_getCategories(self):
        res = self.sn.getCategories()
        assert("SqueakFS" in res)

    def test_getClassMembers(self):
        res = self.sn.getClassMembers("SqueakFS")
        assert("MountPath" in res)
    
    def test_getInstanceMembers(self):
        res = self.sn.getInstanceMembers("BasicClassOrganizer")
        assert("classComment" in res)
        
    def test_getInstanceProtocols(self):
        res = self.sn.getInstanceProtocols("ProtoObject")
        print res
        assert("system primitives" in res and "objects from disk" in res)

    def test_getClassProtocols(self):
        res = self.sn.getClassProtocols("SqueakFS")
        assert("class initialization" in res)
        
    def test_getMethodsInInstanceProtocol(self):
        res = self.sn.getMethodsInInstanceProtocol("SqueakFSNetwork","image reading")
        assert("userActiongetAllClasses" in res and "userActiongetMethodsInInstanceProtocol:InClass:" in res)

    def test_getMethodsInClassProtocol(self):
        res = self.sn.getMethodsInClassProtocol("SqueakFS","mounting and unmounting")
        assert("mount" in res and "mountAt:" in res)
        
    def test_getClassComment(self):
        res = self.sn.getClassComment("SqueakFS")
        assert(len(res) > 40)
    
    def test_getClassesInCategory(self):
        res = self.sn.getClassesInCategory("SqueakFS")
        assert("SqueakFS" in res and "SqueakFSNetwork" in res)
        
    def test_getInstanceMethodsInClass(self):
        res = self.sn.getInstanceMethodsInClass("ProtoObject")
        assert("doOnlyOnce:" in res and "nextInstance" in res and "ifNotNil:ifNil:" in res)

    def test_getClassMethodsInClass(self):    
        res = self.sn.getClassMethodsInClass("SqueakFS")
        assert("initializeClassVariables" in res)
        
    def test_isClassAvailable(self):
        res = self.sn.isClassAvailable("SqueakFS")
        assert(res)
        assert(not self.sn.isClassAvailable("SeeeeeeekKaKaMongabunga"))

    def test_isInstanceMethodAvailable(self):
        res = self.sn.isInstanceMethodAvailable("SqueakFSNetwork","userActionisInstanceMethodAvailable:inClass:")
        assert(res)
        assert(not self.sn.isInstanceMethodAvailable("SqueakFSNetwork","Bmosfoadsfas"))

    def test_getDirectSubClasses(self):
        res = self.sn.getDirectSubClasses("SqueakFSNetwork")
        assert(len(res) == 0)
        res = self.sn.getDirectSubClasses("ProtoObject")
        assert("Object" in res)

    def test_isInstanceProtocolAvailable(self):        
        res  = self.sn.isInstanceProtocolAvailable("network","SqueakFSNetwork")
        assert res
        res  = self.sn.isInstanceProtocolAvailable("neeeeeeetwork","SqueakFSNetwork")
        assert not res
        
    def test_isClassProtocolAvailable(self):
        res = self.sn.isClassProtocolAvailable("kakakakkak","SqueakFS")
        assert not res
        res = self.sn.isClassProtocolAvailable("mounting and unmounting","SqueakFS")
        assert res
    
    def test_isCategoryAvailable(self):
        res = self.sn.isCategoryAvailable("SqueakFS")
        assert(res)
        res = self.sn.isCategoryAvailable("Kernel-Numbers")
        assert(res)
        res = self.sn.isCategoryAvailable("Kernel-KAKAKA,,,}{Numbers")
        assert(not res)
        
    def test_isInstanceMethodInProtocol(self):
        res = self.sn.isInstanceMethodInProtocol("serve:","network","SqueakFSNetwork")
        assert res
        res = self.sn.isInstanceMethodInProtocol("serve:","invalidwtfisthis","SqueakFSNetwork")
        assert not res
        
    def test_isClassMethodInProtocol(self):
        res = self.sn.isClassMethodInProtocol("mount","mounting and unmounting","SqueakFS")
        assert res
        res = self.sn.isClassMethodInProtocol("DoNoMoKaKamount","network","SqueakFS")
        assert not res

    def test_isClassInCategory(self):
        res = self.sn.isClassInCategory("SqueakFS","SqueakFS")
        assert res
        res = self.sn.isClassInCategory("SqueakFS","SqueakFSNetwork")
        assert res
        
    def test_isCategoryAvailable(self):
        res = self.sn.isCategoryAvailable("SqueakFS")
        assert res
        res = self.sn.isCategoryAvailable("NoCategoryWithThisNameIPromise")
        assert not res
    
    def test_getTraits(self):
        """
        Traits is something like a java interface.
        Test that our methods return sensible values
        """
        res = self.sn.getTraits("SqueakFS")
        assert(len(res) == 0)
        res = self.sn.getTraits("Class")
        assert("TBehaviorCategorization" in res and len(res) == 1)
    
    def test_isTrait(self):
        res = self.sn.isTrait("SqueakFS")
        assert not res
        res = self.sn.isTrait("TBehaviorCategorization")
        assert res
        
    def test_getAllTraits(self):
        res = self.sn.getAllTraits()
        assert("TCompilingDescription" in res and "TApplyingOnClassSide" in res)
    
    def test_getTraitUsers(self):
        res = self.sn.getTraitUsers("TCompilingBehavior")
        assert("TPureBehavior" in res)
        
    def test_PerformanceisInstanceMethodAvailable(self):
        for i in range(1,100):
            res = self.sn.isInstanceMethodAvailable("SqueakFSNetwork","userActionisInstanceMethodAvailable:inClass:")
#            assert(res)


    def test_PerformancegetInstanceMethod(self):
        for i in range(1,1000):
            res = self.sn.getInstanceMethod("SqueakFSNetwork","userActionisInstanceMethodAvailable:inClass:")
            assert(res)

    def test_PerformancegetClassMethod(self):
        for i in range(1,1000):
            res = self.sn.getClassMethod("Categorizer","allCategory")
            assert(res)
                        
    def test_PerformanceisClassAvailable(self):
        for i in range(1,100):
            res = self.sn.isClassAvailable("SqueakFS")
            assert(res)

    def test_PerformancegetAllClasses(self):
        for i in range(1,100):
            res = self.sn.getAllClasses()

    def test_getNumberOfClasses(self):
        for i in range(1,100):
            res = self.sn.getNumberOfClasses()
