#!/usr/bin/env python
#
# Visualization Test: Triangle.
# file           : Viz_b.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-31
# last modified  : 2011-07-31

import vtk

# build points
points = vtk.vtkPoints()
points.InsertNextPoint(0.0, 0.0, 0.0)
points.InsertNextPoint(1.0, -1.0, 0.0) # bottom left
points.InsertNextPoint(-1.0, -1.0, 0.0) # bottom right
points.InsertNextPoint(0.0, 1.0, 0.0) # top

pyramid = vtk.vtkPyramid()
pyramid.GetPointIds().SetId(0, 0)
pyramid.GetPointIds().SetId(1, 1)
pyramid.GetPointIds().SetId(2, 2)
pyramid.GetPointIds().SetId(3, 3)
pyramid.GetPointIds().SetId(4, 4)

cells = vtk.vtkCellArray()
cells.InsertNextCell(pyramid)

grid = vtk.vtkUnstructuredGrid()
grid.SetPoints(points)
grid.InsertNextCell(pyramid.GetCellType(), pyramid.GetPointIds())

mapper = vtk.vtkDataSetMapper()
mapper.SetInput(grid)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.8274, 0.2117, 0.5098)
actor.GetProperty().SetLineWidth(2.0)
actor.GetProperty().LightingOff()
actor.GetProperty().SetRepresentationToWireframe()


render = vtk.vtkRenderer()
render.AddActor(actor)
render.GetActiveCamera().Azimuth(180)
render.GetActiveCamera().Elevation(0)
render.GetActiveCamera().Zoom(0.3)
render.SetBackground(0.95, 0.95, 0.95)

window = vtk.vtkRenderWindow()
window.AddRenderer(render)
window.SetSize(600, 450)
window.SetWindowName("Visualization")

#inter = vtk.vtkRenderWindowInteractor()
#inter.SetRenderWindow(window)

#inter.Initialize()
while True:
    window.Render()
#inter.Start()
