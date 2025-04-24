import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Distributions import sim_Bin, ideal_Bin, sim_Geo, ideal_Geo, sim_Normal,ideal_Normal
import numpy as np
from math import sqrt



class GeometricOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        super().__init__(master)
        self.onrelease = onrelease
        self.p = tk.Label(self, text="p", )
        self.pentry = tk.Entry(self)
        self.pentry.bind("<KeyRelease>", self.onKeyRelease)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()


class BinomialOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        super().__init__(master)
        self.onrelease = onrelease
        self.p = tk.Label(self, text="p", )
        self.pentry = tk.Entry(self)
        self.n = tk.Label(self, text="n", )
        self.nentry = tk.Entry(self)
        self.nentry.bind("<KeyRelease>", self.onKeyRelease)
        self.pentry.bind("<KeyRelease>", self.onKeyRelease)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")
        self.n.grid(column=0, row=1, sticky="nsew")
        self.nentry.grid(column=1, row=1, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()


class NormalOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        self.onrelease = onrelease

        super().__init__(master)
        self.mu = tk.Label(self, text="μ", )
        self.muentry = tk.Entry(self)
        self.sig = tk.Label(self, text="σ", )
        self.sigentry = tk.Entry(self)
        self.muentry.bind("<KeyRelease>", self.onKeyRelease)
        self.sigentry.bind("<KeyRelease>", self.onKeyRelease)
        self.place_widgets()

    def place_widgets(self):
        self.mu.grid(column=0, row=0, sticky="nsew")
        self.muentry.grid(column=1, row=0, sticky="nsew")
        self.sig.grid(column=0, row=1, sticky="nsew")
        self.sigentry.grid(column=1, row=1, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()
###errors here
class CalcFrame(tk.Frame):
    def __init__(self, master, distribution):#
        super().__init__(master)
        self.dist=distribution

        self.lradio=tk.Radiobutton(text="P(X<a)")
        self.uradio=tk.Radiobutton(text="P(X>a)")
        self.bradio=tk.Radiobutton(text="P(a<X<b)")
        if self.dist!="Normal":
            self.eradio=tk.Radiobutton(text="P(X=a)")

        self.place_widgets()

    def place_widgets(self):
        self.lradio.grid(column=0, row=0, sticky="nsew")
        self.uradio.grid(column=1, row=0, sticky="nsew")
        self.bradio.grid(column=2, row=0, sticky="nsew")
        if self.dist!="Normal":
            self.eradio.grid(column=3, row=0, sticky="nsew")



class GeometricGFrame(tk.Frame):
    pass


class BinomialGFrame(tk.Frame):
    pass

class NormalGFrame(tk.Frame):
    pass

class Ideal(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.combo = ttk.Combobox(self, width=5, values=["Geometric", "Binomial", "Normal"])
        self.dist = self.combo.get()
        self.current_O_frame = None
        self.current_G_frame = None
        self.current_calc_frame = None
        self.combo.bind("<<ComboboxSelected>>", self.on_dist_change)
        self.calculations = False
        self.calculationsbutton = tk.Button(self, text="show ideal", command=self.showcalculations)
        # self.num = tk.StringVar(value="0")
        # self.numspinbox = ttk.Spinbox(self, width=5, textvariable=self.num, from_=0, to=100, command=self.on_num_change)

        self.place_widgets()

    def place_widgets(self):
        self.combo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        if self.current_O_frame and self.current_G_frame:
            self.current_O_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=10)
            self.current_G_frame.grid(row=0, rowspan=4, column=0, sticky=tk.NSEW, padx=10, pady=10)
            if not self.calculations:
                self.calculationsbutton.grid(row=2,column=1, sticky=tk.NSEW, padx=10, pady=10)
            if self.calculations:
                self.current_calc_frame.grid(row=2,column=1, sticky=tk.NSEW, padx=10, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

    def on_dist_change(self, event):
        self.dist = self.combo.get()  # Update the distribution
        self.change_dist()

    def showcalculations(self):
        if self.calculations == False:
            self.calculations = True
            ### add check boxes for type of calculation < > =
            self.current_calc_frame=CalcFrame(self,self.dist)
            self.refreshG()

    def refreshG(self):
        if self.dist == "Geometric":
            self.current_G_frame = GeometricGFrame(self)
        elif self.dist == "Binomial":
            self.current_G_frame = BinomialGFrame(self)
        elif self.dist == "Normal":
            self.current_G_frame = NormalGFrame(self)

        self.place_widgets()

    def change_dist(self):
        # Destroy the current frame if it exists
        if self.current_O_frame:
            self.current_O_frame.destroy()
        if self.current_G_frame:
            self.current_G_frame.destroy()

        # Create a new frame based on the selected distribution
        if self.dist == "Geometric":
            self.current_O_frame = GeometricOFrame(self, self.refreshG)
            self.current_G_frame = GeometricGFrame(self)
        elif self.dist == "Binomial":
            self.current_O_frame = BinomialOFrame(self, self.refreshG)
            self.current_G_frame = BinomialGFrame(self)
        elif self.dist == "Normal":
            self.current_O_frame = NormalOFrame(self, self.refreshG)
            self.current_G_frame = NormalGFrame(self)

        self.place_widgets()



if __name__ == "__main__":
     root=tk.Tk()
     w=400
     h=300
     root.geometry(f"{w}x{h}+100+100")
     root.resizable(1,1)
     root.title("prototype")
     main_frame=Ideal(root)
     main_frame.pack(fill=tk.BOTH, expand=True)
     root.mainloop()