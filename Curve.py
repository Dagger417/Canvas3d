# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 08:38:23 2020

@author: dgregoriev

This holds a class intended to act as a curve.
A curve is considered as 2 points connected together.

"""
import Point as pt
import Matrix3d as m3
import Coord as cord
import math
import IDmanager as idm

class Line():
    '''
    This represents a joined pair of points. It is able to hold
    directional sense similar to a vector but that sense is not
    utilized until higher elements
    '''
    curveDepot = idm.IDmanager()
    
    def __init__(self,startpt,endpt,**kwargs):
        self.pts = [startpt,endpt]
        
        self.curveid = None
        self.style = StyleLine()
        
        self.curveid = Line.curveDepot.process(self,**kwargs)
        
        self.unitvect = (self.pts[1]-self.pts[0]).unitvect()
    
    
    def in_coordsys(self, targetcoord=cord.Coord.coordsDepot.objDict[0]):
        '''
        this returns an anonymous ID Line with the two coordinates
        transformed to the other coordinate system
        '''
        beginpt = self.pts[0].in_coordsys(targetcoord)
        endpt = self.pts[1].in_coordsys(targetcoord)
        return Line(beginpt,endpt,ID=None)
    
    def __repr__(self):
        
        if(self.pts[0].ptid==None):
            pt0id='None'
        else:
            pt0id = str(self.pts[0].ptid)
        if(self.pts[1].ptid==None):
            pt1id='None'
        else:
            pt1id = str(self.pts[1].ptid)
        retstr ='Point joins ptids: '+pt0id+' to '
        retstr = retstr+pt1id+'\nVector: \n'
        retstr = retstr+str(self.unitvect)
        return retstr
        
        
    
        
        
class StyleLine():
    '''
    This holds the styling for lines
    '''
    def __init__(self):
        self.capstyle = 'round'
        self.fill = 'black'
        self.width = 5
        
if __name__ == "__main__":
    point0 = pt.Point(0,0,0)
    point1 = pt.Point(5,5,0)
    line0 = Line(point0,point1)
    print(line0)
    