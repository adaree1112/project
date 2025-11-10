import tkinter as tk

import mplcursors
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


class DistributionGraph(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def update_plot(self, x_vals, y_vals,graph_type,cdf_vals,showcursors=False):
        self.ax.clear()
        if graph_type == 'bar':
            bars=self.ax.bar(x_vals, y_vals)
            cursor=mplcursors.cursor(bars, hover=True)
            if showcursors:
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"x = {sel.target[0]:.0f}\nP(X=x)={sel.target[1]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)


        if graph_type == 'line':
            plot = self.ax.plot(x_vals, y_vals)
            self.ax.set_ylim(bottom=0)
            self.ax.set_xlim(right=max(x_vals), left=min(x_vals))
            cursor=mplcursors.cursor(plot, hover=True)
            if showcursors:
                @cursor.connect("add")
                def on_add(sel):
                    x, y = sel.target
                    index=np.argmin(np.abs(x_vals - x))
                    sel.annotation.set_text(f"x = {sel.target[0]:.2f}\nP(X<=x)={cdf_vals[index]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)

        self.canvas.draw()

if __name__ == '__main__':
    from Piecewise import Normal, Parameter, Binomial
    mu=Parameter("mu",-999,999,1,0)
    sigma=Parameter("sigma",-999,999,1,1)
    n=Parameter("n",1,999,1,10)
    p=Parameter("p",0,1,0.05,0.5)
    norm=Normal({"mu":mu,"sigma":sigma})
    binom=Binomial({"n":n,"p":p})
    root = tk.Tk()

    graph = DistributionGraph(root,"hi")
    print(binom.get_plot_data())
    graph.update_plot(*norm.get_plot_data(),showcursors=True)
    graph.pack(fill=tk.BOTH, expand=True)
    root.mainloop()