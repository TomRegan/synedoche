#!/usr/bin/env python
#
# Visualization Objects.
# file           : Visualizer.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-03
# last modified  : 2011-08-03

from Interface import UpdateListener
from lib.Enumerations import Colours

from vtk  import vtkDiskSource
from vtk  import vtkActor
from vtk  import vtkPolyDataMapper
from vtk  import vtkRenderer
from vtk  import vtkRenderWindow
#from sys  import getsizeof

class Visualizer(UpdateListener):

    def __init__(self, Monitor):
        self.data={}
        self.monitor = Monitor

    def render(self):
        disk = vtkDiskSource()
        print(self.monitor.data)
        #disk.SetOuterRadius(float(self.monitor.get_int_prop('processor_cycles')))
        disk.SetInnerRadius(0.0)
        disk.SetCircumferentialResolution(30)

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(disk.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(Colours.MAGENTA)
        actor.GetProperty().SetOpacity(0.9)

        renderer = vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(Colours.BASE03)

        window = vtkRenderWindow()
        window.AddRenderer(renderer)
        window.SetSize(900, 400)
            #print(self.monitor.data)
        disk.SetOuterRadius(float(self.monitor.get_int_prop('processor_cycles')))
        window.Render()

    def update(self, *args, **kwargs):
        self.data['registers'].append(kwargs['registers'])

    def add_data_source(self, obj):
        if hasattr(obj, 'register'):
            self.data['registers']=[]
