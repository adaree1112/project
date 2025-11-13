import tkinter as tk


class MegaController:
    def __init__(self, root):
        self.root = root

        self.model=None

        self.graph = tk.Label(bg="black")
        self.cb = tk.Label(bg="grey")
        self.settings=tk.Label(bg="lightgray")
        self.calc=tk.Label(bg="darkgrey")

        self.place_widgets()

    def place_widgets(self):


        self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=(10,5))
        self.settings.grid(row=1, column=1, sticky="nsew",padx=(5,10), pady=(5,5))
        self.calc.grid(row=2, column=1, sticky="nsew",padx=(5,10), pady=(5,10))
        self.graph.grid(row=0, column=0, sticky="nsew", rowspan=3,padx=(10,5), pady=(10,10))
        root.grid_columnconfigure(0, weight=2)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=3)
        root.grid_rowconfigure(2, weight=2)







if __name__ == '__main__':

    root = tk.Tk()
    root.geometry("900x600")

    # 2. Create the Controller, which creates and manages the View
    controller = MegaController(root)

    root.mainloop()