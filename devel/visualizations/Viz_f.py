#!/usr/bin/env python
#
# Graph Vizualization.
# file           : Viz_f.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-01
# last modified  : 2011-08-01

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

graph = vtk.vtkMutableDirectedGraph()

# add vetices
v1 = graph.AddVertex()
v2 = graph.AddVertex()
v3 = graph.AddVertex()
v4 = graph.AddVertex()
v5 = graph.AddVertex()
v6 = graph.AddVertex()

# add edges to graph
graph.AddGraphEdge(v1, v2)
graph.AddGraphEdge(v1, v3)
graph.AddGraphEdge(v1, v4)
graph.AddGraphEdge(v1, v5)
graph.AddGraphEdge(v1, v6)

# an array of vertex sizes
scales = vtk.vtkFloatArray()
scales.SetName("Scales")
scales.InsertNextValue(0.10)
scales.InsertNextValue(0.20)
scales.InsertNextValue(0.15)
scales.InsertNextValue(0.10)
scales.InsertNextValue(0.10)
scales.InsertNextValue(0.10)
scales.InsertNextValue(0.10)

# an array linking colours
colours = vtk.vtkIntArray()
lookup_table = vtk.vtkLookupTable()
colours.SetName("Colours")
colours.InsertNextValue(6)
colours.InsertNextValue(5)
colours.InsertNextValue(4)
colours.InsertNextValue(3)
colours.InsertNextValue(2)
colours.InsertNextValue(1)

graph.GetVertexData().AddArray(scales)
graph.GetVertexData().AddArray(colours)

view = vtk.vtkGraphLayoutView()
view.AddRepresentationFromInput(graph)
view.SetLayoutStrategyToSimple2D()

view.SetScalingArrayName("Scales")
view.SetScaledGlyphs(1)

view.SetVertexColorArrayName("Colours")
view.ColorVerticesOn()

renderer = view.GetRenderer()
renderer.SetBackground(Colours.BASE02)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(600, 450)

view.SetupRenderWindow(window)
window.GetInteractor().Start()