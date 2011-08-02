#!/usr/bin/env python
#
# Testing Visualizer Config.
# file           : Viz_a.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-29
# last modified  : 2011-07-29

import vtk

weights = vtk.vtkDoubleArray()
weights.SetNumberOfComponents(1)
weights.SetName('Weights')

weights.InsertNextValue(1.0)
weights.InsertNextValue(1.0)
weights.InsertNextValue(2.0)

graph = vtk.vtkMutableUndirectedGraph()
v1 = graph.AddVertex()
v2 = graph.AddVertex()
v3 = graph.AddVertex()

graph.AddGraphEdge(v1, v2)
graph.AddGraphEdge(v2, v3)
graph.AddGraphEdge(v1, v3)

graph.GetEdgeData().AddArray(weights)

view = vtk.vtkGraphLayoutView()
view.AddRepresentationFromInput(graph)
view.SetLayoutStrategyToSimple2D()
view.GetLayoutStrategy().SetEdgeWeightField("Weights")
#print '\n'.join(dir(view.GetLayoutStrategy()))
view.SetEdgeLabelArrayName('Weights')
view.SetEdgeLabelVisibility(1)

window = vtk.vtkRenderWindow()
renderer = view.GetRenderer()
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

interactor.Initialize()
window.Render()
interactor.Start()
#print '\n'.join(dir(view.GetRenderer()))
