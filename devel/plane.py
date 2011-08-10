#!/usr/bin/env python
#
# Plane Visualization Element.
# file           : plane.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-10
# last modified  : 2011-08-10

import vtk

line = vtk.vtkLineSource()
line.SetPoint1(1.0, 0.0, 0.0)
line.SetPoint2(0.0, 1.0, 0.0)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(line.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

tube = vtk.vtkTubeFilter()
tube.SetInputConnection(line.GetOutputPort())
tube.SetNumberOfSides(50)

tube_mapper = vtk.vtkPolyDataMapper()
tube_mapper.SetInputConnection(tube.GetOutputPort())

tube_actor = vtk.vtkActor()
tube_actor.SetMapper(tube_mapper)
tube_actor.GetProperty().SetOpacity(0.6)

renderer = vtk.vtkRenderer()
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

renderer.AddActor(actor)
renderer.AddActor(tube_actor)

window.Render()
interactor.Start()
