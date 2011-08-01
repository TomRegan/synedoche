#!/usr/bin/env python
#
# Graph Viz Test.
# file           : Viz_c.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-31
# last modified  : 2011-07-31

from vtk import vtkGraphLayoutView
from vtk import vtkRandomGraphSource
from vtk import vtkRenderWindow
from vtk import vtkRenderWindowInteractor

source = vtkRandomGraphSource()
view = vtkGraphLayoutView()
view.SetVertexLabelArrayName("VertexDegree")
view.SetVertexLabelVisibility(True)

representation = view.AddRepresentationFromInputConnection(
    source.GetOutputPort())

window = vtkRenderWindow()

view.SetupRenderWindow(window)

window.GetInteractor().Start()
