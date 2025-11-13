import tkinter as tk
from importlib.metadata import Distribution

import mplcursors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from project.DraggablePoint import DraggablePoint
from project.LabelSpinbox import LabelSpinbox, PairRadioButton


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
    def __init__(self, master, controller, showcursors=False):
        super().__init__(master)
        self.controller = controller
        self.showcursors = showcursors
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def update_plot(self, x_vals, y_vals,graph_type,cdf_vals):
        self.ax.clear()
        if graph_type == 'bar':
            bars=self.ax.bar(x_vals, y_vals)
            if self.showcursors:
                cursor = mplcursors.cursor(bars, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"x = {sel.target[0]:.0f}\nP(X=x)={sel.target[1]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)


        if graph_type == 'line':
            plot = self.ax.plot(x_vals, y_vals)
            self.ax.set_ylim(bottom=0)
            self.ax.set_xlim(right=max(x_vals), left=min(x_vals))
            if self.showcursors:
                cursor = mplcursors.cursor(plot, hover=True)

                @cursor.connect("add")
                def on_add(sel):
                    x, y = sel.target
                    index=np.argmin(np.abs(x_vals - x))
                    sel.annotation.set_text(f"x = {sel.target[0]:.2f}\nP(X<=x)={cdf_vals[index]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)

        self.canvas.draw()


class DistributionSettingsFrame(tk.Frame):
    def __init__(self, master, controller,parameters,on_change):
        super().__init__(master)
        self.controller = controller
        self.on_change = on_change

        for param in parameters:
            LabelSpinbox(self,param,self.on_change).pack()

class PiecewiseSettingsFrame(tk.Frame):
    def __init__(self, master, controller,on_change,add,remove):
        super().__init__(master)
        self.rbs=PairRadioButton(self,["Linear","Cubic Splines"],on_change)
        self.add_button = tk.Button(text="Add Point", command=add)
        self.remove_button = tk.Button(text="Remove Point", command=remove)

        self.place_widgets()

    def place_widgets(self):
        self.rbs.grid(column=0, row=0)
        self.add_button.grid(column=0, row=1)
        self.remove_button.grid(column=0, row=2)



if __name__ == '__main__':
    from Piecewise import Parameter
    def cb(option=None):
        print("hello",option)
    def add():
        print("add")
    def remove():
        print("remove")
    root = tk.Tk()
    #settings=DistributionSettingsFrame(root,None,[Parameter("mu",-999,999,1,0),Parameter("sigma",-999,999,1,1)],cb)
    settings=PiecewiseSettingsFrame(root,None,cb,add,remove)
    settings.grid(column=0, row=0)
    root.mainloop()


    """
    from Piecewise import Normal, Parameter, Binomial
    mu=Parameter("mu",-999,999,1,0)
    sigma=Parameter("sigma",-999,999,1,1)
    n=Parameter("n",1,999,1,10)
    p=Parameter("p",0,1,0.05,0.5)
    norm=Normal({"mu":mu,"sigma":sigma})
    binom=Binomial({"n":n,"p":p})
    root = tk.Tk()

    graph = DistributionGraph(root,"hi",showcursors=False)
    graph.update_plot(*norm.get_plot_data())
    graph.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
    """