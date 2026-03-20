import tkinter as tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraphTest(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.axes.plot(x:=np.linspace(-100,100,1000),x**2)

if __name__ == '__main__':
    root = tk.Tk()
    app = GraphTest(root)
    app.pack()
    root.mainloop()