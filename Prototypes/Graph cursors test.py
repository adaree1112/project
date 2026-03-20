import tkinter as tk

import numpy as np
from matplotlib.backend_bases import cursors
from matplotlib.backend_tools import Cursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mplcursors import cursor

class GraphTest(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        line,=self.axes.plot(x:=np.linspace(-100,100,1000),x**2)

        cursors=cursor(line,hover=True)

        @cursors.connect("add")
        def on_add(sel):
            x, y = sel.target
            sel.annotation.set_text(f"x={x:.2f}\ny={y:.2f}")
            #sel.annotation.set_text(f"x={x:.2f}\ny+1={y+1:.2f}") #This line is uncommented for second part


if __name__ == '__main__':
    root = tk.Tk()
    app = GraphTest(root)
    app.pack()
    root.mainloop()