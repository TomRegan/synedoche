#!/usr/bin/env python
#
# Multiple Undirected Graph.
# file           : Graphics.py
# author         : Tom Regan <noreply.tom.regan@gmail.com>
# since          : 2011-08-09
# last modified  : 2011-08-09

MAXSIZE = 30

from Interface import UpdateListener
from lib.Enumerations import Colours
try:
    from vtk import vtkDiskSource
    from vtk import vtkLineSource
    from vtk import vtkPolyDataMapper
    from vtk import vtkActor
    from vtk import vtkTubeFilter
    from vtk import vtkFollower
    from vtk import vtkRenderer
    from vtk import vtkRenderWindow
    from vtk import vtkRenderWindowInteractor
    from vtk import vtkVectorText
    from vtk import vtkFileOutputWindow
    from vtk import vtkOutputWindow
except ImportError, e:
    import sys
    sys.stderr.write("Couldn't locate dependency: vtk. Cannot draw.\n")

class BaseVisualizer(UpdateListener):
    def update(self):
        pass
    def render(self):
        pass
    def initialize(self, *args):
        pass

class Visualizer(BaseVisualizer):
    def __init__(self):
        # Dynamically altered data
        self.poly_data = []
        self.bar_data  = []

        # Static poly data
        self.resize_factor = []

        # Mappers for rendering
        self.poly_mappers = []
        self.line_mappers = []
        self.text_mappers = []
        self.bar_mappers  = []

        # Actor objects
        self.actors = []
        self.dynamic_actors = [[], []]

        # Actor Properties
        self.edge_colours = []
        self.node_ids     = []

        # TODO: Make layout grids an enumeration. (2011-08-09)
        self.layout_grid = [
            [  0.0,   0.0,  0.0],
            [  0.0,  40.0,  0.0],
            [-30.0, -30.0,  0.0],
            [ 30.0, -30.0,  0.0],
            [ 40.0,  20.0,  0.0],
            [-40.0,  20.0,  0.0]
        ]

        # Data
        self.data = []
        self.updated = False

        # Broadcast sources
        self.broadcasters = []

        # Other Attributes
        self.node_layout_strategy = None
        self.edge_layout_strategy = None
        self.text_layout_strategy = None

        # Get rid of pointless warnings
        out = vtkFileOutputWindow()
        out.SetFileName(".vtkMessageLog.log")
        vtkOutputWindow.SetInstance(out)

        # Initialize window
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)

        self.window = vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.window.SetSize(600, 600)

        self.interactor = vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

    def __del__(self):
        for broadcaster in self.broadcasters:
            broadcaster.remove(self)
        del self

#
# Public Interface
#

    def update(self, source):
        """Updates the data source."""
        # TODO: Review: does this need to loop?
        # Maybe we can just append list as-is? (2011-08-22)

        # Create some storage space for the new data.
        self.data.append([])
        # Push each item into the array on the stack.
        try:
            for item in source:
                self.data[-1].append(item)
        except:
            # If that fails, assume one piece of data.
            self.data[-1].append(source)
        self.updated = True

    def add_node(self, source, name="", resize=1.0):
        """Appends a node to the nodes list."""
        # Poly-data
        self.node_ids.append(name)
        poly = vtkDiskSource()
        # Set initial size and resize factor
        self.resize_factor.append(resize)
        try:
            size = self.data[-1][source]
        except:
            size = 0
        poly.SetOuterRadius(size)
        poly.SetInnerRadius(size - 0.4)
        poly.SetRadialResolution(30)
        poly.SetCircumferentialResolution(30)
        self.poly_data.append(poly)
        # Mapper
        poly_mapper = vtkPolyDataMapper()
        poly_mapper.SetInputConnection(poly.GetOutputPort())
        self.poly_mappers.append(poly_mapper)

    def add_edge(self, start, end, colour=Colours.BASE0):
        """Appends an edge to the edges list."""
        # Line
        line = vtkLineSource()
        line.SetPoint1(start)
        line.SetPoint2(end)
        # Line Mapper
        line_mapper = vtkPolyDataMapper()
        line_mapper.SetInputConnection(line.GetOutputPort())
        self.edge_colours.append(colour)
        self.line_mappers.append(line_mapper)
        # Bar
        bar = vtkTubeFilter()
        bar.SetInputConnection(line.GetOutputPort())
        bar.SetRadius(2.5)
        self.bar_data.append(bar)
        # Bar Mapper
        # Tried this, but mapping the ribbon caused beaucoup errors,
        # debugging would take a week.There must be some kind of way
        # out of here.
        # Said the joker to the thief
        # There's too much confusion
        # I can't get no relief
        # No reason to get excited, the thief he kindly spoke
        # But you and I have been through that
        # And this is not our fate
        # So let us not talk falsely now, the hour is getting late.
        # (2011-08-12)
        bar_mapper = vtkPolyDataMapper()
        bar_mapper.SetInputConnection(bar.GetOutputPort())
        self.bar_mappers.append(bar_mapper)

    def add_text(self, message):
        """Appends text to the text list."""
        # Text
        text = vtkVectorText()
        text.SetText(message)
        # Mapper
        text_mapper = vtkPolyDataMapper()
        text_mapper.SetInputConnection(text.GetOutputPort())
        self.text_mappers.append(text_mapper)

    def initialize(self, *args):
        """Sets a window title and creates objects from mapped polydata."""
        try:
            self.window.SetWindowName(args[0])
        except: pass
        self._draw_nodes()
        self._draw_edges()
        self._draw_text()

    def render(self):
        if self.updated:
            self._redraw()
        self.updated = False
        for actor in self.actors:
            self.renderer.AddActor(actor)
        self.window.Render()

    def get_edge_layout_strategy(self):
        return str(self.edge_layout_strategy)

    def get_text_layout_strategy(self):
        return str(self.text_layout_strategy)

    def set_edge_layout_hub(self):
        """Adds edges to the graph originating from the initial vertex."""
        for i in range(len(self.poly_mappers)):
            self.add_edge(self.layout_grid[0], self.layout_grid[i])
        self.edge_layout_strategy = "hub"

    def set_text_layout_default(self):
        """Adds labels to the graph attached to each vertex."""
        for i in range(len(self.poly_mappers)):
            self.add_text(self.node_ids[i])
        self.text_layout_strategy = "default"

#
# Worker Functions
#

    def _redraw(self):
        for i in range(len(self.poly_data)):
            # Redraw the vertices
            poly = self.poly_data[i]
            ribbon = self.dynamic_actors[0][i]
            polact = self.dynamic_actors[1][i]
            try:
                size = self.data[-1][i]
            except:
                size = 0
            size = size * self.resize_factor[i]

            if size < MAXSIZE:
                poly.SetOuterRadius(size)
                poly.SetInnerRadius(size - 0.4)
            else:
                # Create instead an inwardly filling disc.
                poly.SetInnerRadius(MAXSIZE - size/40)
                polact.GetProperty().SetOpacity(0.3)

            # Redraw the bars: recolour to reflect +/- change.
            try:
                data = self.bar_data[i]
                cur = self.data[-1][i]
                old = self.data[-2][i]
                #print("cur:{:}, old:{:}".format(cur, old))
                dif = abs(cur - old)+2
                if (cur - old) < 0:
                    ribbon.GetProperty().SetColor(Colours.BLUE)
                elif (cur - old) == 0:
                    ribbon.GetProperty().SetColor(Colours.MAGENTA)
                else:
                    ribbon.GetProperty().SetColor(Colours.GREEN)
                data.SetRadius(dif)
            except: pass

    def _draw_nodes(self):
        self.nodes = []
        for i in range(len(self.poly_mappers)):
            actor = vtkActor()
            actor.SetMapper(self.poly_mappers[i])
            actor.SetPosition(self.layout_grid[i])
            actor.GetProperty().SetColor(Colours.BASE0)
            actor.GetProperty().SetOpacity(0.6)
            self.actors.append(actor)
            self.dynamic_actors[1].append(actor)

    def _draw_edges(self):
        for i in range(len(self.line_mappers)):
            # Edges
            edge_actor = vtkActor()
            edge_actor.SetMapper(self.line_mappers[i])
            edge_actor.GetProperty().SetColor(self.edge_colours[i])
            edge_actor.GetProperty().SetOpacity(0.8)
            edge_actor.GetProperty().SetLineWidth(1)
            self.actors.append(edge_actor)
            # Bars
            bar_actor = vtkActor()
            bar_actor.GetProperty().SetInterpolationToFlat()
            bar_actor.SetMapper(self.bar_mappers[i])
            bar_actor.GetProperty().SetColor(Colours.MAGENTA)
            bar_actor.GetProperty().SetOpacity(0.2)
            self.actors.append(bar_actor)
            self.dynamic_actors[0].append(bar_actor)


    def _draw_text(self):
        for i in range(len(self.text_mappers)):
            actor = vtkFollower()
            actor.SetMapper(self.text_mappers[i])
            actor.GetProperty().SetColor(Colours.BASE02)
            actor.SetScale(2.0, 2.0, 2.0)
            # Tweak to shift the text a little more central
            pos = [x-5.0 for x in self.layout_grid[i]]
            actor.AddPosition(pos)
            self.actors.append(actor)


if __name__ == '__main__':
    counter1 = 8
    counter2 = 6
    counter3 = 4
    counter4 = 3
    counter5 = 5
    counter6 = 7
    vis = Visualizer()
    vis.add_node(0, "Anne")
    vis.add_node(1, "Bob")
    vis.add_node(2, "Carol")
    vis.add_node(3, "David")
    vis.add_node(4, "Eleanor")
    vis.add_node(5, "Fred")
    vis.set_edge_layout_hub()
    vis.set_text_layout_default()
    vis.initialize("Visualizer")
    for i in range(100):
        vis.update([counter1, counter2, counter3,
                    counter4, counter5, counter6])
        vis.render()
        counter1 = counter1 + 0.1
        if i % 10 == 0:
            counter4 = counter4 + 1
