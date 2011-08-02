#!/usr/bin/env python
#
# Graph Vizualization.
# file           : Viz_f.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-01
# last modified  : 2011-08-01


import vtk

graph = vtk.vtkMutableUndirectedGraph()

v1 = graph.AddVertex()
v2 = graph.AddVertex()
v3 = graph.AddVertex()
v4 = graph.AddVertex()
v5 = graph.AddVertex()

# add edges to graph
graph.AddGraphEdge(v1, v2)
graph.AddGraphEdge(v2, v3)
graph.AddGraphEdge(v3, v4)
graph.AddGraphEdge(v4, v5)

print("Number of vertices: {:}".format(graph.GetNumberOfVertices()))
print("Number of Edges: {:}".format(graph.GetNumberOfEdges()))

view = vtk.vtkGraphLayoutView()
view.AddRepresentationFromInput(graph)
view.SetVertexLabelArrayName("VertexDegree")
view.SetLayoutStrategyToForceDirected()
view.VertexLabelVisibilityOn()
view.ColorEdgesOn()

window = vtk.vtkRenderWindow()
renderer = view.GetRenderer()
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

window = vtk.vtkRenderWindow()
window.SetSize(600, 450)

view.SetupRenderWindow(window)

window.GetInteractor().Start()
#interactor.Initialize()
#window.Render()
#interactor.Start()
