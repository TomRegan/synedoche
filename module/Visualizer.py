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
from vtk  import vtkRenderWindowInteractor
#from sys  import getsizeof

class Visualizer(UpdateListener):

    def __init__(self, Monitor):
        self.data={}
        self.monitor = Monitor
        self.value = 0

        self.graphic = vtkDiskSource()
        self.graphic.SetOuterRadius(0.1)
        self.graphic.SetInnerRadius(0.0)
        self.graphic.SetCircumferentialResolution(30)

        self.mapper = vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.graphic.GetOutputPort())

        self.actor = vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(Colours.BLUE)
        self.actor.GetProperty().SetOpacity(0.9)

        self.renderer = vtkRenderer()
        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(Colours.BASE03)
        self.renderer.GetActiveCamera().Azimuth(1)

        self.window = vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.window.SetSize(900, 400)
        #self.graphic.SetOuterRadius(
        #    float(self.monitor.get_int_prop('processor_cycles')))
        self.interactor = vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

    def render(self):
        self.value = self.value + 1
        self.graphic.SetOuterRadius(float(self.value)/1000)
        self.window.Render()

    def change(self):
        self.graphic.SetOuterRadius(
            float(self.monitor.get_int_prop('processor_cycles')))

    def update(self, *args, **kwargs):
        self.data['registers'].append(kwargs['registers'])

    def add_data_source(self, obj):
        if hasattr(obj, 'register'):
            self.data['registers']=[]
