#!/usr/bin/env python
#
# Underected Graph Using vtkGlyphs.
# file           : glyph.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-08-08
# last modified  : 2011-08-08

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

# Create a set of points
points = vtk.vtkPoints()
points.InsertNextPoint(5.0, 0.0, 0.0)
points.InsertNextPoint(0.0, 0.0, 0.0)
points.InsertNextPoint(-5.0, 0.0, 0.0)

# Create an array of scales
scales = vtk.vtkFloatArray()
scales.SetName("scales")
scales.InsertNextValue(2.0)
scales.InsertNextValue(2.0)
scales.InsertNextValue(3.0)

# Colours
lookup_table = vtk.vtkLookupTable()
lookup_table.Build()
lookup_table.SetNumberOfTableValues(10)
lookup_table.SetTableValue(0     , 0     , 0     , 0, 1)#Black
lookup_table.SetTableValue(1, 0.8900, 0.8100, 0.3400, 1)#Banana
lookup_table.SetTableValue(2, 1.0000, 0.3882, 0.2784, 1)#Tomato
lookup_table.SetTableValue(3, 0.9608, 0.8706, 0.7020, 1)#Wheat
lookup_table.SetTableValue(4, 0.9020, 0.9020, 0.9804, 1)#Lavender
lookup_table.SetTableValue(5, 1.0000, 0.4900, 0.2500, 1)#Flesh
lookup_table.SetTableValue(6, 0.5300, 0.1500, 0.3400, 1)#Raspberry
lookup_table.SetTableValue(7, 0.9804, 0.5020, 0.4471, 1)#Salmon
lookup_table.SetTableValue(8, 0.7400, 0.9900, 0.7900, 1)#Mint
lookup_table.SetTableValue(9, 0.2000, 0.6300, 0.7900, 1)#Peacock

# Combine into polydata
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.GetPointData().SetScalars(scales)
#print(polydata.GetPointData())

# Build the glpyh
shape = vtk.vtkSphereSource()
shape.SetThetaResolution(30)
shape.SetPhiResolution(30)
glyph = vtk.vtkGlyph3D()
glyph.SetColorModeToColorByVector()
glyph.SetScaleModeToScaleByScalar()
glyph.SetSource(shape.GetOutput())
glyph.SetInput(polydata)
glyph.Update()

# Mapper and actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(glyph.GetOutputPort())
mapper.SetScalarRange(0, 8)
mapper.SetLookupTable(lookup_table)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer   = vtk.vtkRenderer()
window     = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()

window.AddRenderer(renderer)
interactor.SetRenderWindow(window)

# Add actor
renderer.AddActor(actor)
renderer.SetBackground(Colours.BASE03)

window.SetSize(600, 600)

window.Render()
interactor.Start()
