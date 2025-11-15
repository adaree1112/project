import tkinter as tk
from functools import partial

from PiecewiseGraph import ComboboxFrame

class MegaController:
    def __init__(self, root):
        self.root = root

        self.model=None


        self.graph = tk.Label(bg="black")
        self.cb = ComboboxFrame(self.root, ["Normal","Binomial"],self.set_distribution)
        self.settings=tk.Label(bg="lightgray")
        self.calc=tk.Label(bg="darkgrey")

        self.place_widgets()

    def set_distribution(self, dist_type):
        print("hello")
        print(dist_type)
        match dist_type:
            case "Normal":
                self.cb.setdefinition("X~B(n,p)")
            case "Binomial":
                self.cb.setdefinition("X~")


    def place_widgets(self):
        self.graph.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(10,5), pady=10)
        self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
        self.calc.grid(row=2, column=1, sticky="nsew", padx=(5,10),pady=(5,10))

        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=2)







if __name__ == '__main__':

    root = tk.Tk()
    root.geometry("900x600")

    # 2. Create the Controller, which creates and manages the View
    controller = MegaController(root)

    root.mainloop()