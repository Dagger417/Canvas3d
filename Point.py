# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:40:59 2020

@author: dgregoriev

This holds a class intended to act as a point.
A point is considered a 3 space object. The intent of this class
is to act as a base for math amnipulation of data

"""

#import pint as pint
import Matrix3d as m3
import Coord as cord
import math
import IDmanager as idm

class Point(m3.Vector3d):
    '''
    Point represents a 3 space coordinate in a specific Coordinate System
    '''
    pointDepot = idm.IDmanager()

    def __init__(self,i=0,j=0,k=0,coord=cord.Coord.coordsDepot.objDict[0],**kwargs):
        super().__init__(i,j,k)
        self.loc = m3.Vector3d(i,j,k)
        self.coord = coord
        self.ptid = None
        self.style = StylePoint()
        
        for entry in kwargs:
            formatentry = entry.lower()
            if formatentry=='id':
                pass
        
        self.ptid = Point.pointDepot.process(self,**kwargs)
            
        
    def in_coordsys(self, targetcoord=cord.Coord.coordsDepot.objDict[0]):
        '''
        this returns an anonymous ID Point with the coordinates
        transformed to the other coordinate system
        '''
        #this starts by obtaining the transform to global
        toglob = self.coord.getTransToGlob()
        
        #now the point is placed into 4d
        localpt4d = m3.Matrix4d(direct=[[self.matrix[0][0]],[self.matrix[1][0]], 
                                      [self.matrix[2][0]],[1]])
        
        globpt = toglob*localpt4d
        
        totarget = targetcoord.getTransToGlob().inv()
        
        newpt = totarget*globpt
        
        return Point(newpt.matrix[0][0],newpt.matrix[1][0],newpt.matrix[2][0], 
                     coord=targetcoord,ID=None)
        
    def __sub__(self,other):
        '''
        This handles requests for the distance between points.
        This converts to a global reference frame and returns a Vector3d
        with the difference
        '''
        globown = self.coord.getTransToGlob().inv()
        #now the point is placed into 4d
        self4d = m3.Matrix4d(direct=[[self.matrix[0][0]],[self.matrix[1][0]], 
                                      [self.matrix[2][0]],[1]])
        other4d = m3.Matrix4d(direct=[[other.matrix[0][0]],[other.matrix[1][0]], 
                                      [other.matrix[2][0]],[1]])
        
        globpt = globown*self4d
        totarget = other.coord.getTransToGlob().inv()
        
        newpt = totarget*other4d
        retmatr = globpt-newpt
        return m3.Vector3d(retmatr.matrix[0][0],retmatr.matrix[1][0], 
                           retmatr.matrix[2][0])
        


class StylePoint():
    '''
    This class contains all the visual style point attributes
    The reference frame is the native coordinate system of the point
    '''
    def __init__(self):
        
        self.fill = '#000fff000'
        #self.fill = None
        self.outline = '#000000'
        self.outlinethkness = 2
        self.shape = 'circle'
        self.globradius = 5
     

if __name__ == "__main__":
    
    base = cord.CoordRect()
    sec = cord.CoordPolar(base=base)
    #sec.rotate_k_coordsys(math.pi/4)
    sec.scale_coordsys(.25)
    #print(sec.getTransToGlob())
    #sec.translate_coordsys(1,1,1)
    #print(sec.getTransToGlob())
    print('\n\n')
    #vectx = m3.Vector3d(1,1,0)
    #vecty = m3.Vector3d(-1,1,0)
    vectx = m3.Vector3d(1,math.pi/4,0)
    vecty = m3.Vector3d(1,2*(math.pi/4),0)
    third = cord.CoordRect(base=sec,parent=sec, vects=(vectx,vecty))
    
    basept = Point(1,0,0,coord=third)
    print(basept.in_coordsys())
    #print(third.getTransToGlob())
    
    sec.rotate_k_coordsys(math.pi/4)
    print(basept.in_coordsys())
    #print(third.getTransToGlob())
    
    