# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 09:49:24 2020

@author: dgregoriev

This is a UI module meant to handle transforms to display
geometry content on the Canvas widget

"""

try:
    #if python 2.7 is used this will work
    import Tkinter as tk
except ModuleNotFoundError:
    #this means its a 3.x interpreter
    import tkinter as tk
    import tkinter.ttk as ttk

import Point as pt
import math
import Matrix3d as m3
import Coord as cord
import Curve as curv


class ViewingPlane():
    '''
    This is a model coordinate system object that represents the
    model coordinate system plane to which the model location data
    will be projected for a view
    '''
    def __init__(self):
        '''
        model coord0
        view rotation
        view translate (move)
        view scale (zoom)
        view center offset (centerpt)
        '''
        self.vcord0 = cord.Coord.coordsDepot.objDict[0]
        self.vtranslate = cord.CoordRect(id=None,base=self.vcord0,parent=self.vcord0)
        self.vrotate = cord.CoordRect(id=None,base=self.vtranslate,parent=self.vtranslate)
        self.vscale = cord.CoordRect(id=None,base=self.vrotate,parent=self.vrotate)
        self.vieweroff = cord.CoordRect(id=None,base=self.vscale,parent=self.vscale)
        self.vscale.scale_coordsys(2)
            
    def screenresized(screenw, screenh):
        '''
        This takes the width and height of the screen and adjusts
        the vieweroff to center the 0,0 point
        '''
        pass

class UIpoint():
    '''
    This class represents the UI point that's drawn to the screen
    This is called on to create the persistant point as well
    '''
    def __init__(self,canvasobj,x,y,z):
    
        self.datapt = pt.Point(x,y,z)
        self.canvasobj = canvasobj
        self.view = self.canvasobj.viewer
        self.style = self.datapt.style
        #create a second point that is a screen projected version
        self.scrnpt = self.datapt.in_coordsys(targetcoord = self.view.vieweroff)
        self.visible = True
        self.canvaspoint = None
        #self.refresh()
        
    def refresh(self):
        '''
        This function forces the screenpoint to refresh
        '''
        #get the proper size of the pt
        ptscrnsize = m3.Vector3d(self.style.globradius,0,0)        
        ptscrnsize = self.view.vscale.getTransToGlob().inv()*ptscrnsize
        ptscrnsize = self.view.vrotate.getTransToGlob()*ptscrnsize
        ptscrnsize = math.sqrt((ptscrnsize.T()*ptscrnsize).matrix[0][0]-1)
        self.scrnpt = self.datapt.in_coordsys(self.view.vieweroff)
        
        leftedge = self.scrnpt.matrix[0][0]-ptscrnsize
        topedge = self.scrnpt.matrix[1][0]-ptscrnsize
        rightedge = self.scrnpt.matrix[0][0]+ptscrnsize
        bottomedge = self.scrnpt.matrix[1][0]+ptscrnsize
        self.canvasobj.delete(self.canvaspoint)
        #print(str(leftedge)+' '+str(topedge)+' '+str(rightedge)+' '+str(bottomedge))
        self.canvaspoint = self.canvasobj.create_oval(leftedge, topedge, 
                           rightedge, bottomedge, outline=self.style.outline, 
                           fill=self.style.fill, 
                           width=self.style.outlinethkness, activefill='yellow')

class UIline():
    '''
    This class represents the UI line that's drawn to the screen
    '''
    def __init__(self,canvasobj,pt0,pt1):
        #.create_oval(10, 10, 80, 80, outline="#f11",
        #                   fill="#1f1", width=2)
        self.uipts = [pt0,pt1]
        self.dataline = curv.Line(pt0.datapt,pt1.datapt)
        self.canvasobj = canvasobj
        self.view = self.canvasobj.viewer
        self.style = self.dataline.style
        #create a second line that is a screen projected version
        self.scrnline = self.dataline.in_coordsys(targetcoord = self.view.vieweroff)
        self.visible = True
        self.canvasline = None
        #self.refresh()
        
        
    def refresh(self):
        '''
        This function forces the screenline to refresh
        '''
        self.scrnline = self.dataline.in_coordsys(targetcoord = self.view.vieweroff)
        pt0 = self.scrnline.pts[0]
        pt0xy = (pt0.matrix[0][0],pt0.matrix[1][0])
        pt1 = self.scrnline.pts[1]
        pt1xy = (pt1.matrix[0][0],pt1.matrix[1][0])
        self.canvasobj.delete(self.canvasline)
        self.canvasline = self.canvasobj.create_line(pt0xy[0],pt0xy[1],pt1xy[0]
                                   ,pt1xy[1],width=self.style.width, 
                                   fill=self.style.fill, 
                                   capstyle=self.style.capstyle, activefill='yellow')
        

class Canvas3d(tk.Canvas):
    '''
    This class is meant to be able to receive global data and
    convert that to canvas data able to be viewed on the screen.
    The goal is that any needed conversion to display is hidden
    '''
    def __init__(self,parent=None,**kwargs):
        
        
        #first extract the canvas width and height from the arguments
        #self.width = 200
        #self.height = 200
        #self.width = self.winfo_reqwidth()
        #self.height = self.winfo_reqheight()
        super().__init__(master=parent,**kwargs)
        #self.config(width=self.width, height=self.height,highlightthickness=0)
        self.config(highlightthickness=0)
        
        self.uipointlist = []
        self.uilinelist = []
        
        self.viewer = ViewingPlane()
        
        self.bind('<Configure>',self.on_resize)
        self.centerview()
        
        class translate_event():
            #this class handles pan events
            #it is designed as a singleton
            startx = None
            starty = None
            #shiftkeyheld
            canvasobj = self
            def evnt_lmpressed(event):
                translate_event.startx = event.x
                translate_event.starty = event.y
            def evnt_lmholddrag(event):
                diffx = event.x-translate_event.startx
                diffy = event.y-translate_event.starty
                translate_event.startx = event.x
                translate_event.starty = event.y
                self.viewer.vtranslate.translate_coordsys(diffx,diffy)
                translate_event.canvasobj.redraw()
            def evnt_lmshiftpressed(event):
                #get the starting point
                translate_event.startx = event.x
                translate_event.starty = event.y
            def evnt_lmshiftdrag(event):
                translate_event.canvasobj.update()
                halframewidth = translate_event.canvasobj.winfo_reqwidth()*10
                halframeheight = translate_event.canvasobj.winfo_reqheight()*10
                diffx = event.x-translate_event.startx
                diffy = event.y-translate_event.starty
                ratiox = diffx/halframewidth
                radx = (-1)*(math.pi)*ratiox
                ratioy = diffy/halframeheight
                rady = (-1)*(math.pi)*ratioy
                self.viewer.vrotate.rotate_j_coordsys(radx)
                self.viewer.vrotate.rotate_i_coordsys(rady)
                translate_event.canvasobj.redraw()
            def evnt_lmctrlpressed(event):
                translate_event.startx = event.x
                translate_event.starty = event.y
            def evnt_lmctrldrag(event):
                halframeheight = translate_event.canvasobj.winfo_reqheight()*10
                diffy = event.y-translate_event.starty
                ratioy = (-1)*(diffy/halframeheight)+1
                self.viewer.vscale.scale_coordsys(ratioy)
                translate_event.canvasobj.redraw()
            
        
        self.bind('<Button-1>',translate_event.evnt_lmpressed)
        self.bind('<B1-Motion>',translate_event.evnt_lmholddrag)
        self.bind('<Shift-Button-1>',translate_event.evnt_lmshiftpressed)
        self.bind('<Shift-B1-Motion>',translate_event.evnt_lmshiftdrag)
        self.bind('<Control-Button-1>',translate_event.evnt_lmctrlpressed)
        self.bind('<Control-B1-Motion>',translate_event.evnt_lmctrldrag)
        
        
        self.viewer.vrotate.rotate_k_coordsys(math.pi/4)
        self.viewer.vrotate.rotate_i_coordsys(math.pi/4)
        
        
        
        #topleft = pt.Point(0,0,0)
        #topright = pt.Point(50,0,0)
        #bottomright = pt.Point(50,-50,0)
        #bottomleft = pt.Point(0,-50,0)
        
        
        self.scrnpt0 = UIpoint(self,0,0,0)
        self.scrnpt1 = UIpoint(self,50,0,0)
        self.scrnpt2 = UIpoint(self,50,-50,0)
        self.scrnpt3 = UIpoint(self,0,-50,0)
        
        
        self.scrnline0 = UIline(self,self.scrnpt0,self.scrnpt1)
        self.scrnline1 = UIline(self,self.scrnpt1,self.scrnpt2)
        self.scrnline2 = UIline(self,self.scrnpt2,self.scrnpt3)
        self.scrnline3 = UIline(self,self.scrnpt3,self.scrnpt0)
        
        self.redraw()
        
        
        
        '''
        scrnpt1 = UIpoint(topright,self)
        scrnpt2 = UIpoint(bottomright,self)
        scrnpt3 = UIpoint(bottomleft,self)
        '''
        
        
        
    def redraw(self):
        '''
        This function dumps the view and redraws the full screen
        
        '''
        
        self.scrnline0.refresh()
        self.scrnline1.refresh()
        self.scrnline2.refresh()
        self.scrnline3.refresh()
        self.scrnpt0.refresh()
        
    def centerview(self):
        '''
        This centers the view on the 0,0,0 point, resetting the viewer offset
        '''
        self.update()
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        #reset any camera moves
        self.viewer.vtranslate.own_exp_to_coord0list = []
        #since screen coords have +y facing down, we spin the coord sys
        self.viewer.vtranslate.rotate_i_coordsys(math.pi)#spin the coord sys
        xtranslate = self.width/2
        ytranslate = self.height/2
        self.viewer.vtranslate.translate_coordsys(xtranslate,ytranslate,0)
        
    def on_resize(self, event):
        '''
        capture the new dimensions of the canvas
        '''
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
    

if __name__ == "__main__":
    root = tk.Tk()
    inputpanel = Canvas3d(root)
    #root.update()
    inputpanel.centerview()
    #inputpanel.grid(row=0, sticky='S')
    inputpanel.pack(fill=tk.BOTH, expand=tk.YES)
    root.mainloop()