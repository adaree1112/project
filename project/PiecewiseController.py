import tkinter as tk
import tkinter.ttk as ttk
from re import match
from tkinter import Spinbox

from project.Piecewise import Piecewise, AbstractStatisticalModel, Binomial, Exponential
from project.PiecewiseGraph import PiecewiseGraph
from project.spinertest import LabelSpinBox

class PiecewiseController:
    def __init__(self,root):
        self.model = Piecewise([(2,3),(3,2),(4,4)])

        # The Controller creates the View
        self.graph = PiecewiseGraph(root, self)
        self.graph.pack(fill=tk.BOTH, expand=True)

        ##wont be here eventually
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="Add Point", command=self.handle_add_point).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Remove Point", command=self.handle_remove_point).pack(side=tk.LEFT)
        tk.Button(button_frame,text="Normalise",command=self.normalise).pack(side=tk.LEFT)

        self.update_view()

    def update_view(self):
        points = self.model.get_points()
        self.model.calculate_pieces()
        self.graph.update_plot(points, self.model.pieces)

    def handle_add_point(self):
        self.model.add_point()
        self.update_view()

    def handle_remove_point(self):
        self.model.remove_point()
        self.update_view()

    def normalise(self):
        self.model.normalise()
        self.update_view()

    def point_moved(self,old_x,old_y,new_x,new_y):
        self.model.update_point(old_x,old_y,new_x,new_y)
        self.update_view()

class StatsticalButtonFrame(tk.Frame):
    def __init__(self,root,refresh,parameters=None):
        super().__init__(root)
        for i,(k,v) in enumerate(parameters.items()):
            LabelSpinBox(self,k,0,1,0.01,0.5,refresh).pack(side=tk.TOP)






# --- A P P L I C A T I O N   S T A R T U P ---

if __name__ == '__main__':
    points = [(0, 0), (1, 2), (2, 1.5)]

    root = tk.Tk()
    root.title("MVC Piecewise Spline Graph")

    # 2. Create the Controller, which creates and manages the View
    controller = PiecewiseController(root)

    root.mainloop()