import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from piecewisecubicsplines import piecewise_cubic_spline,piecewise_linear
import random

class DraggablePoint:
    def __init__(self, coord,refresh_callback):
        self.x,self.y= coord
        self.refresh_callback = refresh_callback
        self.artist=None
        self.press = None

    def attach (self,ax):
        self.artist,=ax.plot(self.x,self.y,'ro',picker=5)
        self.connect()

    def connect(self):
        fig = self.artist.figure
        self.cidpress = fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = fig.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_press(self, event):
        if event.inaxes != self.artist.axes:
            return
        contains, _ = self.artist.contains(event)
        if not contains:
            return
        x0, y0 = self.artist.get_data()
        self.press = (x0[0], y0[0]), (event.xdata, event.ydata)

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.artist.axes:
            return
        (x0, y0), (xpress, ypress) = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.x = x0 + dx
        self.y = max(y0 + dy,0)
        self.artist.set_data([self.x], [self.y])
        self.artist.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.artist.figure.canvas.draw()
        self.refresh_callback()

    def get_coords(self):
        return self.x, self.y


class PiecewiseGraph(tk.Frame):
    def __init__(self, master,coords):
        super().__init__(master)
        self.fig = Figure(figsize = (5, 5), dpi = 100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()

        self.points = [DraggablePoint(coord,self.refresh) for coord in coords]
        self.add_point()
        self.refresh()

    def add_point(self):
        coords=[point.get_coords() for point in self.points]
        currx,curry=zip(*coords)
        self.points.append(DraggablePoint((random.uniform(min(currx),max(currx)),random.uniform(min(curry),max(curry))),self.refresh))
        self.refresh()

    def remove_point(self):
        self.points.remove(random.choice(list(self.points)))
        self.refresh()

    def refresh(self):
        self.ax.clear()

        for point in self.points:
            point.attach(self.ax)

        coords=[point.get_coords() for point in self.points]
        print(coords)
        x,y=zip(*coords)
        self.ax.plot(x,y,'ro')

        self.pieces=piecewise_cubic_spline(coords)

        for piece in self.pieces:
            lower, upper, a, b, c, d, = piece
            x = np.linspace(lower, upper, 50)
            y = a * x ** 3 + b * x ** 2 + c * x + d

            self.ax.plot(x, y)
        self.ax.set_ylim(bottom=0)

        self.canvas.draw()



points=[(0,0),(1,2),(2,1.5)]
pieces=[]

root = tk.Tk()
root.title("Adding points")
graph_page = PiecewiseGraph(root,points)

graph_page.pack()
root.mainloop()