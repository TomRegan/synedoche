#!/usr/bin/env python
#
# Visualization of data as a disk.
# file           : disk.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-02
# last modified  : 2011-08-02

import vtk
import time

class Colours(set):
    BASE03  = [0.0000, 0.1686, 0.2117]
    BASE02  = [0.0274, 0.2117, 0.2588]
    BASE01  = [0.3450, 0.4313, 0.4588]
    BASE00  = [0.3960, 0.4823, 0.5137]
    BASE0   = [0.5137, 0.5803, 0.5882]
    BASE1   = [0.5764, 0.6313, 0.6313]
    BASE2   = [0.9333, 0.9098, 0.8352]
    BASE3   = [0.9921, 0.9647, 0.8901]
    YELLOW  = [0.7098, 0.5372, 0.0000]
    ORANGE  = [0.7960, 0.3941, 0.0862]
    RED     = [0.8627, 0.1960, 0.1843]
    MAGENTA = [0.8274, 0.2117, 0.5098]
    VIOLET  = [0.4235, 0.4431, 0.7686]
    BLUE    = [0.1490, 0.5450, 0.8235]
    CYAN    = [0.1647, 0.6313, 0.5960]
    GREEN   = [0.5215, 0.6000, 0.0000]
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

disk = vtk.vtkDiskSource()
disk.SetOuterRadius(2.0)
disk.SetInnerRadius(0.0)
disk.SetCircumferentialResolution(30)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(disk.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(Colours.MAGENTA)
actor.GetProperty().SetOpacity(0.9)

renderer = vtk.vtkRenderer()
renderer.AddActor( actor )
renderer.SetBackground(Colours.BASE03)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer( renderer )
renWin.SetSize( 900, 400 )


for i in range(100):
    disk.SetOuterRadius(float(i)/1000)
    renWin.Render()
    time.sleep(0.5)
