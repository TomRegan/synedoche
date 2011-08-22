#!/usr/bin/env python
#
# Visualization Objects.
# file           : Visualizer.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-03
# last modified  : 2011-08-04

from Interface import UpdateListener
from lib.Enumerations import Colours

try:
    from vtk import vtkActor
    from vtk import vtkLineSource
    from vtk import vtkPolyDataMapper
    from vtk import vtkRenderer
    from vtk import vtkRenderWindow
    from vtk import vtkRenderWindowInteractor
    from vtk import vtkBalloonWidget
    from vtk import vtkBalloonRepresentation
except ImportError:
    print("Cannot start visualizer: VTK libraries could not be found.")

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
        self.initialized     = False
        self.monitor         = Monitor
        self.sources         = []
        self.representations = []
        self.resize_factors  = []
        self.actors          = []
        self.lines           = []
        self.mappers         = []

        self.representation_count = 0
        self.layout_grid = [
            [ 0.0,  0.0,  0.0],
            [-3.0,  3.0,  0.0],
            [ 3.0,  3.0,  0.0],
            [-4.0, -2.0,  0.0],
            [ 4.0, -2.0,  0.0],
            [ 0.0, -4.0,  0.0]
        ]

    def __del__(self):
        for source in self.sources:
            source.remove(self)
        del self

#
# Interface
#

    def initialize(self, name='Visualizer', link_render=False):
        """Initialize creates a render and window required before
        the visualization can be displayed."""
        self._init_renderer()
        self._init_window(name=name)
        #self._init_balloons()
        self.initialized = True
        self.link_render = link_render

    def update(self, *args, **kwargs):
        """Called by broadcaster object, not public interface."""
        #self.sources['registers'].append(kwargs['registers'])
        if self.link_render:
            self.render()

    def render(self):
        """Render causes the visualization display to update.

        Usage:
            render should be called whenever there is new/updated
            data to display, eg: once per client cycle.
        """
        cycles = self.monitor.get_int_prop('processor_cycles')
        for rep in self.representations:
            size = self.resize_factors[self.representations.index(rep)]
            rep.SetRadius(float(cycles)/size)
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
            obj.register(self)
            self.sources.append(obj)

    def add_representation_from_data(self,
                                     int_prop,
                                     opacity=1.0,
                                     position=None,
                                     colour="blue",
                                     resize_factor=1.0):
        if self.representation_count >= len(self.layout_grid):
            return
        if hasattr(self.monitor, 'get_int_prop'):
            self.monitor.get_int_prop(int_prop)
            self.representations.append(self._init_representation())
            try:
                colour = getattr(Colours, colour.upper())
            except:
                colour = Colours.BLUE
            if position == None:
                position = self.layout_grid[self.representation_count]
            self._add_line(self.layout_grid[0], position)
            self._init_mapper()
            self._init_actor(opacity=opacity,
                             colour=colour,
                             position=position
                            )
            self.representation_count = self.representation_count + 1

#
# Accessor Functions
#

    def is_initialized(self):
        return self.initialized

#
# Worker Functions
#
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
            representation.Update()
        except: pass
        return representation

    def _init_actor(self,
                    colour,
                    opacity,
                    position
                   ):
        p = position
        actor = vtkActor()
        actor.SetMapper(self.representation_mapper)
        actor.GetProperty().SetColor(colour)
        actor.GetProperty().SetOpacity(opacity)
        actor.SetPosition(p[0], p[1], p[2])
        self.actors.append(actor)
        #actor.GetProperty().SetInterpolationToFlat()
        #actor.GetProperty().EdgeVisibilityOn()
        #actor.GetProperty().SetEdgeColor(Colours.BASE3)

    def _init_lines(self):
        # FIX: Nothing to do with lines is working. (2011-08-08)
        actor = vtkActor()
        actor.SetMapper(self.line_mapper)
        actor.GetProperty().SetLineWidth(4)
        self.actors.append(actor)

    def _init_mapper(self):
        self.representation_mapper = vtkPolyDataMapper()
        self.representation_mapper.SetInputConnection(
            self.representations[0].GetOutputPort())
        # FIX: Nothing to do with lines is working. (2011-08-08)
        self.line_mapper = vtkPolyDataMapper()
        self.line_mapper.SetInputConnection(
            self.lines[0].GetOutputPort())

    def _init_renderer(self):
        self.renderer = vtkRenderer()
        for actor in self.actors:
            self.renderer.AddActor(actor)
        self.renderer.SetBackground(Colours.BASE03)
        # Automatically set the camera to a pleasing sort of position.
        self.renderer.ResetCamera()

    def _init_window(self, dimx=640, dimy=640, name=''):
        self.window = vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.window.SetSize(dimx, dimy)
        self.interactor = vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)
        self.window.SetWindowName(name)

    def _init_balloons(self):
        for actor in self.actors:
            balloon = vtkBalloonRepresentation()
            balloon.SetBalloonLayoutToImageRight()
            widget = vtkBalloonWidget()
            widget.SetRepresentation(balloon)
            widget.SetInteractor(self.interactor)
            widget.AddBalloon(actor, "This is a sphere")
            widget.EnabledOn()


    def _add_line(self, start, end):
        # FIX: Nothing to do with lines is working. (2011-08-08)
        line = vtkLineSource()
        line.SetPoint1(start)
        line.SetPoint2(end)
        line.Update()
        self.lines.append(line)
