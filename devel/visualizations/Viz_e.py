#!/usr/bin/env python
#
# Structured Grid Visualization.
# file           : Viz_e.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-01
# last modified  : 2011-08-01

from vtk import vtkStructuredGrid
from vtk import vtkPoints
from vtk import vtkPolyDataMapper
from vtk import vtkActor
from vtk import vtkRenderWindow
from vtk import vtkRenderer
from vtk import vtkStructuredGridOutlineFilter
from vtk import vtkRenderWindowInteractor

numi = 2
numj = 2
numk = 2

grid  = vtkStructuredGrid()
points = vtkPoints()

for k in range(numk):
    for j in range(numj):
        for i in range(numi):
            points.InsertNextPoint(i, j, k)
            print("{:}:{:}:{:}".format(i, j, k))
points.InsertNextPoint(1.5, 1.5, 1.5)

grid.SetDimensions(2, 2, 2)
grid.SetPoints(points)

print("There are {:} points.".format(grid.GetNumberOfPoints()))
print("There are {:} cells.".format(grid.GetNumberOfCells()))

outline_filter = vtkStructuredGridOutlineFilter()
outline_filter.SetInputConnection(grid.GetProducerPort())
outline_filter.Update()

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(outline_filter.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

renderer = vtkRenderer()
renderer.AddActor(actor)

window   = vtkRenderWindow()
window.AddRenderer(renderer)

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

window.Render()
interactor.Start()

