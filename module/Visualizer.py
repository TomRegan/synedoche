#!/usr/bin/env python
#
# Visualization Objects.
# file           : Visualizer.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-03
# last modified  : 2011-08-04

from Interface import UpdateListener
from lib.Enumerations import Colours

from vtk  import vtkActor
from vtk  import vtkPolyDataMapper
from vtk  import vtkRenderer
from vtk  import vtkRenderWindow
from vtk  import vtkRenderWindowInteractor
#from vtk  import vtkInteractorStyleTrackballActor
#from sys  import getsizeof

class UnknownRepresentationException(Exception):
    """Tried to call a representation (vtkSource) that doesn't exist."""
    pass

class Visualizer(UpdateListener):
    """Displays representations of data.

    Usage:
        m = Monitor.Monitor()
        v = Visualizer.Visualizer(m)
        v.add_representation_from_data('processor_cycles')
        v.initialize('Window Name')
        for i in range(100):
            v.render()
    """

    def __init__(self, Monitor):
        self.sources={}
        self.monitor = Monitor
        self.representations=[]
        self.actors=[]
        self.mappers=[]

#
# Interface
#

    def initialize(self, name='Vizualizer'):
        """Initialize creates a render and window required before
        the visualization can be displayed."""
        self._init_renderer()
        self._init_window(name=name)

    def render(self):
        """Render causes the visualization display to update.

        Usage:
            render should be called whenever there is new/updated
            data to display, eg: once per client cycle.
        """
        cycles = self.monitor.get_int_prop('processor_cycles')
        for rep in self.representations:
            rep.SetRadius(float(cycles)/1000)
        self.window.Render()

    def add_broadcast_data_source(self, obj):
        """Registers the Visualizer with a broadcaster which must
        implement the `register' method. Fails silently.

        Usage:
            v = Visualizer.Visualizer()
            p = Processor.Pipelined()
            v.add_broadcast_data_source(p)
        """
        if hasattr(obj, 'register'):
            self.sources['registers']=[]

    def add_representation_from_data(self,
                                     int_prop,
                                     opacity=1.0,
                                     position=[0, 0, 0],
                                     colour="blue"):
        if hasattr(self.monitor, 'get_int_prop'):
            self.monitor.get_int_prop(int_prop)
            self.representations.append(self._init_representation())
            try:
                colour = getattr(Colours, colour.upper())
            except:
                colour = Colours.BLUE
            self._init_mapper()
            self._init_actor(opacity=opacity,
                             colour=colour,
                             position=position
                            )

    def add_representation_from_broadcast_data(self, source):
        pass

    def add_representation_from_source(self, source):
        pass

#
# Worker Functions
#
    def update(self, *args, **kwargs):
        """Called by broadcaster object, not public interface."""
        self.sources['registers'].append(kwargs['registers'])

    def _init_representation(self, name='sphere'):
        import vtk
        # stage the name
        rname = 'vtk' + name.title() + 'Source'
        call = getattr(vtk, rname)
        try:
            representation = call()
        except Exception, e:
            raise UnknownRepresentationException(e.message)
        try:
            representation.SetRadius(1.0)
            representation.SetThetaResolution(20)
            representation.SetPhiResolution(20)
            #representation.SetCentre([0.0, 0.0, 0.0])
            #representation.SetInnerRadius(0.0)
            #representation.SetCircumferentialResolution(30)
        except: pass
        return representation

    def _init_actor(self,
                    colour=Colours.BLUE,
                    opacity=1.0,
                    position=[0, 0, 0]
                   ):
        p = position
        actor = vtkActor()
        actor.SetMapper(self.mapper)
        actor.GetProperty().SetColor(colour)
        actor.GetProperty().SetOpacity(opacity)
        actor.SetPosition(p[0], p[1], p[2])
        self.actors.append(actor)
        #actor.GetProperty().SetInterpolationToFlat()
        #actor.GetProperty().EdgeVisibilityOn()
        #actor.GetProperty().SetEdgeColor(Colours.BASE3)

    def _init_mapper(self):
        self.mapper = vtkPolyDataMapper()
        self.mapper.SetInputConnection(
            self.representations[0].GetOutputPort())

    def _init_renderer(self):
        self.renderer = vtkRenderer()
        for actor in self.actors:
            self.renderer.AddActor(actor)
        self.renderer.SetBackground(Colours.BASE03)
        self.renderer.GetActiveCamera().Azimuth(1)

    def _init_window(self, dimx=640, dimy=640, name=''):
        self.window = vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.window.SetSize(dimx, dimy)
        # Fix: Style isn't achieving anything. (2011-08-04)
        #self.style = vtkInteractorStyleTrackballActor()
        self.interactor = vtkRenderWindowInteractor()
        #self.interactor.SetInteractorStyle(self.style)
        self.interactor.SetRenderWindow(self.window)
        self.window.SetWindowName(name)

