import tkinter as tk
from tkinter import ttk

class GeometricOFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.p = tk.Label(self, text="p",)
        self.pentry = tk.Entry(self)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")

class BinomialOFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.p = tk.Label(self, text="p",)
        self.pentry = tk.Entry(self)
        self.n = tk.Label(self, text="n",)
        self.nentry = tk.Entry(self)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")
        self.n.grid(column=0, row=1, sticky="nsew")
        self.nentry.grid(column=1, row=1, sticky="nsew")

class NormalOFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.mu = tk.Label(self, text="μ",)
        self.muentry = tk.Entry(self)
        self.sig = tk.Label(self, text="σ",)
        self.sigentry = tk.Entry(self)

        self.place_widgets()

    def place_widgets(self):
        self.mu.grid(column=0, row=0, sticky="nsew")
        self.muentry.grid(column=1, row=0, sticky="nsew")
        self.sig.grid(column=0, row=1, sticky="nsew")
        self.sigentry.grid(column=1, row=1, sticky="nsew")

class GeometricGFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="Geometric Distribution", bg="lightblue")
        self.label.pack(expand=True)

class BinomialGFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="Binomial Distribution", bg="lightgreen")
        self.label.pack(expand=True)

class NormalGFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="Normal Distribution", bg="lightyellow")
        self.label.pack(expand=True)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.combo=ttk.Combobox(self, width=5, values=["Geometric","Binomial","Normal"])
        self.dist=self.combo.get()
        self.current_O_frame = None
        self.current_G_frame = None
        self.combo.bind("<<ComboboxSelected>>", self.on_dist_change)
        self.place_widgets()

    def place_widgets(self):
        self.combo.grid(row=0, column=1, sticky=tk.EW,padx=10, pady=10)
        if self.current_O_frame and self.current_G_frame:
            self.current_O_frame.grid(row=1, column=1, sticky=tk.NSEW,padx=10, pady=10)
            self.current_G_frame.grid(row=0,rowspan=4, column=0, sticky=tk.NSEW,padx=10, pady=10)


        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

    def on_dist_change(self, event):
        self.dist = self.combo.get()  # Update the distribution
        self.change_frame()

    def change_frame(self):
        # Destroy the current frame if it exists
        if self.current_O_frame:
            self.current_O_frame.destroy()
        if self.current_G_frame:
            self.current_G_frame.destroy()

        # Create a new frame based on the selected distribution
        if self.dist == "Geometric":
            self.current_O_frame = GeometricOFrame(self)
            self.current_G_frame = GeometricGFrame(self)
        elif self.dist == "Binomial":
            self.current_O_frame = BinomialOFrame(self)
            self.current_G_frame = BinomialGFrame(self)
        elif self.dist == "Normal":
            self.current_O_frame = NormalOFrame(self)
            self.current_G_frame = NormalGFrame(self)

        self.place_widgets()


if __name__ == "__main__":
    root=tk.Tk()
    w=400
    h=300
    root.geometry(f"{w}x{h}+100+100")
    root.resizable(1,1)
    root.title("prototype")
    main_frame=Application(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
