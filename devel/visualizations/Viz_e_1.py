#!/usr/bin/env python
#
# Colouring Points.
# file           : Viz_e_1.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-08-02
# last modified  : 2011-08-02

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

import vtk

renderer = vtk.vtkRenderer()
renderer.SetBackground(Colours.BASE02)
window   = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(600, 450)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

source = vtk.vtkPointSource()
source.SetCenter(0, 0, 0)
source.SetNumberOfPoints(5)
source.SetRadius(5.0)
source.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInput(source.GetOutput())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(5)
actor.GetProperty().SetOpacity(0.9)
actor.GetProperty().SetColor(Colours.RED)

renderer.AddActor(actor)

interactor.Initialize()
window.Render()
interactor.Start()
