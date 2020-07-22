# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:53:54 2020

@author: dgregoriev

This holds a class intended to act as a repository of Coordinate systems.
Any transformations performed on a coordinate system to arrive at a
derived coordinate system

"""


import Matrix3d as m3
import math
import IDmanager as idm
class Coord:
    '''
    This is a base class for the various coordinate systems
    The coord ID=0 is the base eulerian class with a simple x,y,z orientation
    All transforms in other classes hold their transform necessary to come 
    back to the coord ID=0 class.
    Coord()
    Coord(vects)
    Coord(base=cord) #this is defining a base coordinate system for the new coordinate system
    Coord(ID=desiredID) #if id is included in the list of variables then it is set to the value,
        if ID=None, then it is an anonymous id, if not included in the variable list, then
        an autoID is generated for the Coord
    Coord(cordfuncts=[funct,funct,funct]) #this is a list of functions 
    Coord(parent=Coord) #this is defined when cascading/linked coord systems are desired
    '''
    coordsDepot = idm.IDmanager()
    
    def __init__(self,**kwargs):
        '''
        a'=M(x)
        where M is the 4d transformation matrix 
        '''
        self.coordfunctstrans = [self.to_cartx,self.to_carty,self.to_cartz]
        self.inheri_trans_to_coord0 = None
        self.own_exp_to_coord0list=[]
        self.childcoordslist = []
        
        vectfrombase = None
        #idflag = False
        parent=self
        basecoord = None
        for entry in kwargs:
            formatentry = entry.lower()
            if formatentry=='id':
                pass            
            elif formatentry=='base':
                basecoord = kwargs[entry]
                validinst = isinstance(basecoord,Coord)
                if(validinst==True):
                    #transfer the list to transform the base system
                    #back to the coord0 system
                    #make sure it is a copy by value
                    self.inheri_trans_to_coord0=basecoord.getTransToGlob()
                    parent = basecoord
                else:
                    raise('base must be a valid Coord object')
            elif(formatentry=='vects'):
                #means list/tuple of vectors passed
                vectfrombase = kwargs[entry]
            elif(formatentry=='cordfuncts'):
                self.coordfunctstrans = kwargs[entry]
            elif(formatentry=='parent'):
                #means the coord system should be tied to changes in another
                #coord system. tell the parent to log the child
                kwargs[entry].childcoordslist.append(self)
            else:
                raise('definition of coordinate system not acceptable')
                
        #set the ID
        self.coordID = Coord.coordsDepot.process(self,**kwargs)
        '''
        if idflag==False:
            #means no mention was made of the id, so we auto-populate it
            available = False
            while available == False:
                Coord.nextid = Coord.nextid+1
                available = Coord.coordDict.get(Coord.nextid)
            self.coordID = Coord.nextid
            Coord.coordDict[self.coordID] = self
        '''
        #now if there is a defining vector set we apply it
        if vectfrombase!=None:
            #first get the missing k vector
            xval = parent.coordfunctstrans[0](vectfrombase[0])
            yval = parent.coordfunctstrans[1](vectfrombase[0])
            zval = parent.coordfunctstrans[2](vectfrombase[0])
            ivect = m3.Vector3d(xval,yval,zval)
            ivect = ivect.unitvect()
            xval = parent.coordfunctstrans[0](vectfrombase[1])
            yval = parent.coordfunctstrans[1](vectfrombase[1])
            zval = parent.coordfunctstrans[2](vectfrombase[1])
            jvect = m3.Vector3d(xval,yval,zval)
            jvect = jvect.unitvect()
            kvect = ivect.cross(jvect).unitvect()
            
            #we aren't sure that the original jvect was ortho to ivect
            #so we set that here
            jvect = kvect.cross(ivect).unitvect()
            # for this transformation: I=AX
            # or... A^(-1)=X where X is the column vectors
            # ivect, jvect, and kvect
            a_invmatrix = []
            '''
            a_matrix.append([ivect.matrix[0][0], jvect.matrix[0][0], kvect.matrix[0][0],0])
            a_matrix.append([ivect.matrix[1][0], jvect.matrix[1][0], kvect.matrix[1][0],0])
            a_matrix.append([ivect.matrix[2][0], jvect.matrix[2][0], kvect.matrix[2][0],0])
            a_matrix.append([0,0,0,1])
            '''
            a_invmatrix.append([ivect.matrix[0][0], ivect.matrix[1][0], ivect.matrix[2][0],0])
            a_invmatrix.append([jvect.matrix[0][0], jvect.matrix[1][0], jvect.matrix[2][0],0])
            a_invmatrix.append([kvect.matrix[1][0], kvect.matrix[1][0], kvect.matrix[2][0],0])
            a_invmatrix.append([0,0,0,1])
            self.own_exp_to_coord0list.insert(0,m3.Matrix4d(direct=a_invmatrix))
            
    def _vectinvalid(self,vectin):
            validinst = isinstance(vectin,m3.Matrix3d)
            if(validinst!=True):
                raise('input must be an input vector')
            if vectin.numcols()!=1:
                raise('input must be vector form')
    def to_cartx(self,vectin):
        #this takes the vector and returns a cartesian version x value
        #validate the vectin
        self._vectinvalid(vectin)
        return vectin.matrix[0][0]
    def to_carty(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        return vectin.matrix[1][0]
    def to_cartz(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        return vectin.matrix[2][0]
    
    def translate_coordsys(self,idist=0,jdist=0,kdist=0):
        '''
        This translates in place the coordinate system and logs the inverse
        to the self.trans_to_coord0list
        '''
        transmatrix = m3.Matrix4d.trans_matrix(idist,jdist,kdist)
        self.own_exp_to_coord0list.insert(0,transmatrix.inv())
        #now update children if necessary
        self.updatechildren()
        
    def rotate_i_coordsys(self,theta_i=0):
        '''
        This rotates in place the coordinate system about the i axis and
        logs the inverse to the self.trans_to_coord0list
        '''
        rotmatrix = m3.Matrix4d.rot_i_matrix(theta_i)
        self.own_exp_to_coord0list.insert(0,rotmatrix.inv())
        #now update children if necessary
        self.updatechildren()
        
    def rotate_j_coordsys(self,phi_j=0):
        '''
        This rotates in place the coordinate system about the j axis and
        logs the inverse to the self.trans_to_coord0list
        '''
        rotmatrix = m3.Matrix4d.rot_j_matrix(phi_j)
        self.own_exp_to_coord0list.insert(0,rotmatrix.inv())
        #now update children if necessary
        self.updatechildren()
        
    def rotate_k_coordsys(self,gamma_k=0):
        '''
        This rotates in place the coordinate system about the k axis and
        logs the inverse to the self.trans_to_coord0list
        '''
        rotmatrix = m3.Matrix4d.rot_k_matrix(gamma_k)
        self.own_exp_to_coord0list.insert(0,rotmatrix.inv())
        #now update children if necessary
        self.updatechildren()
        
    def scale_coordsys(self,scale=1):
        '''
        This scales in place the coordinate system about the system's origin
        and logs the inverse to the self.trans_to_coord0list
        '''
        scalmatrix = m3.Matrix4d.scale_matrix(scale)
        self.own_exp_to_coord0list.insert(0,scalmatrix.inv())
        #now update children if necessary
        self.updatechildren()
            
    def getTransToGlob(self):
        '''
        this returns the matrix that is the transform to put coordinates
        in this system, back into global coordinates
        '''
        #multiply out the list of transforms
        retmatrix = m3.Matrix4d(direct=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        for entry in self.own_exp_to_coord0list:
            if entry==None:
                continue
            retmatrix = entry*retmatrix
        if self.inheri_trans_to_coord0!=None:
            retmatrix = retmatrix*self.inheri_trans_to_coord0
        return retmatrix
    def toRectCoords(self,vectin):
        '''
        This function returns a vector that represents the rectangular
        coordinate from the same i,j,k orientation of the coord system
        '''
        return vectin
    def updatechildren(self):
        '''
        This method is intended to update children of changes made to their
        predecessor's matrix
        '''
        for child in self.childcoordslist:
            child.inheri_trans_to_coord0 = self.getTransToGlob()
            child.updatechildren()

class CoordRect(Coord):
    '''
    CoordRect represents a 3 space Eulerian coordinate system
    '''
    def __init__(self,**kwargs):
        '''
        List of valid input arguments:
        CoordRect() #**this is only valid for the first Coord0**
        CoordRect(vects=[Vector3d, Vector3d]) #<ivec, jvec, (implied kvec)>
        CoordRect(base=Coord) #base coordinate system that this will evolve from
        CoordRect(id=desiredID)
        '''
        coordfunctstrans = [self.to_cartx,self.to_carty,self.to_cartz]
        
        super().__init__(**dict(kwargs, cordfuncts=coordfunctstrans))
        


class CoordPolar(Coord):
    '''
        List of valid input arguments:
        CoordPolar(vects=[Vector3d, Vector3d]) #<ivec, jvec, (implied kvec)>
        CoordPolar(base=Coord) #base coordinate system that this will evolve from
        CoordPolar(id=desiredID)
    '''    
    
    def __init__(self,**kwargs):
        
        coordfunctstrans = [self.to_cartx,self.to_carty,self.to_cartz]
        super().__init__(**dict(kwargs, cordfuncts=coordfunctstrans))
    
    def to_cartx(self,vectin):
        #this takes the vector and returns a cartesian version x value
        #validate the vectin
        self._vectinvalid(vectin)
        xret = vectin.matrix[0][0]*math.cos(vectin.matrix[1][0])
        return xret
    def to_carty(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        yret = vectin.matrix[0][0]*math.sin(vectin.matrix[1][0])
        return yret
    def to_cartz(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        return vectin.matrix[2][0]

class CoordSpherical(Coord):
    '''
        List of valid input arguments:
        CoordSpherical(vects=[Vector3d, Vector3d]) #<ivec, jvec, (implied kvec)>
        CoordSpherical(base=Coord) #base coordinate system that this will evolve from
        CoordSpherical(id=desiredID)
        spherical coords is <R, theta(inclination), gamma (azimuth)>
    '''
    def __init__(self, **kwargs):
        self.coordfunctstrans = [self.to_cartx,self.to_carty,self.to_cartz]
        super().__init__(**dict(kwargs, cordfuncts=self.coordfunctstrans))
    
    def to_cartx(self,vectin):
        #this takes the vector and returns a cartesian version x value
        #validate the vectin
        self._vectinvalid(vectin)
        xret = vectin.matrix[0][0]*math.sin(vectin.matrix[1][0])*math.cos(vectin.matrix[2][0])
        return xret
    def to_carty(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        yret = vectin.matrix[0][0]*math.sin(vectin.matrix[1][0])*math.sin(vectin.matrix[2][0])
        return yret
    def to_cartz(self,vectin):
        #validate the vectin
        self._vectinvalid(vectin)
        zret = vectin.matrix[0][0]*math.cos(vectin.matrix[1][0])
        return zret
        
#There should always be a 0 space coordinate system to base everything off of
CoordRect()

if __name__ == "__main__":
    base = CoordRect()
    sec = CoordPolar(base=base)
    sec.rotate_i_coordsys(math.pi/4)
    print(sec.getTransToGlob())
    #sec.translate_coordsys(1,1,1)
    #print(sec.getTransToGlob())
    print('\n\n')
    #vectx = m3.Vector3d(1,1,0)
    #vecty = m3.Vector3d(-1,1,0)
    vectx = m3.Vector3d(1,2*math.pi/4,0)
    vecty = m3.Vector3d(1,3*(math.pi/4),0)
    #third = CoordRect(ID=None,base=sec,parent=sec, vects=(vectx,vecty))
    third = CoordRect(ID=None,base=sec,parent=sec)
    print(third.getTransToGlob())
    sec.rotate_i_coordsys(math.pi/4)
    
    print(third.getTransToGlob())
    
    #print(third.coordID)

