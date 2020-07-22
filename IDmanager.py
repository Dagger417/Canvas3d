# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 03:33:52 2020

@author: Schadenfreude

This module holds methods for id managment 
"""

class IDmanager():
    '''
    This class handles the management of id values for the
    classes it serves. It will generally be assigned to a class
    variable accessible to all instances it represents
    '''
    

    def __init__(self):
        self.objDict = {}
        self.nextid = -1
        
        
    def process(self,entity,**kwargs):
        '''
        This function processes whether an ID is warranted and issues
        the ID if requested storing the entity as the referenced item
        '''
        idflag = False
        for entry in kwargs:
            formatentry = entry.lower()
            if formatentry=='id':
                desigID = kwargs[entry]
                idflag = True
                #check if it is not None
                if desigID!=None:
                    #log it into the dict
                    objid = desigID
                    self.objDict[objid] = entity
                else:
                    #implied None
                    objid = desigID
        #set the ID if not identified
        if idflag==False:
            #means no mention was made of the id, so we auto-populate it
            available = False
            while available == False:
                self.nextid = self.nextid+1
                available = self.objDict.get(self.nextid)
            objid = self.nextid
            self.objDict[objid] = entity
        return objid
            
if __name__ == "__main__":
    
    other = IDmanager()
    print(other.process(5,ID=12))
    print(other.process(5,ID=None))
    print(other.process(5))
    print(other.objDict)