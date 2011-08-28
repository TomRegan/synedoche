#!/usr/bin/env python
#
# Bubble Widget.
# file           : bubble.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-08-08
# last modified  : 2011-08-08

import vtk

sphere = vtk.vtkSphereSource()
sphere.SetCenter(-4.0, 0.0, 0.0)
sphere.SetRadius(4.0)
sphere.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(sphere.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
window   = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()

window.AddRenderer(renderer)
interactor.SetRenderWindow(window)

balloon = vtk.vtkBalloonRepresentation()
balloon.SetBalloonLayoutToImageRight()

widget = vtk.vtkBalloonWidget()
widget.SetRepresentation(balloon)
widget.SetInteractor(interactor)
widget.AddBalloon(actor, "This is a sphere")

renderer.AddActor(actor)
window.Render()
window.SetSize(600, 600)
widget.EnabledOn()

interactor.Start()
