import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from project.DraggablePoint import DraggablePoint

class PiecewiseGraph(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

        self.draggable_points = []

    def update_plot(self, points, pieces):
        self.ax.clear()
        self.draggable_points = []

        for coord in points:
            point = DraggablePoint(coord, self.controller)
            point.attach(self.ax)
            self.draggable_points.append(point)

        x, y = zip(*points)
        self.ax.plot(x, y, 'ro')

        for piece in pieces:
            lower, upper, a, b, c, d, = piece
            x = np.linspace(lower, upper, 50)
            y = a * x ** 3 + b * x ** 2 + c * x + d
            self.ax.plot(x, y, 'b-')

        self.ax.set_ylim(bottom=0)
        self.ax.autoscale_view()
        self.canvas.draw()