import tkinter as tk
from tkinter import ttk

import mplcursors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from project.Piecewise import Normal, Piecewise
from project.DraggablePoint import DraggablePoint
from project.LaTeXformulaimage import latex_to_tk_image
from project.LabelSpinbox import LabelSpinbox, PairRadioButton


class PiecewiseGraph(tk.Frame):
    def __init__(self, master, controller,add_point):
        super().__init__(master)
        self.controller = controller
        self.add_point = add_point
        self.showcursors = True

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.canvas.get_tk_widget().bind("<Double-Button-1>", self.add_point_on_click)

        self.draggable_points = []

    def update_plot(self, points, pieces,cdf_func=None,shadeinclmin=None,shadeinclmax=None):
        if shadeinclmin is not None or shadeinclmax is not None:
            if shadeinclmin is None:
                shadeinclmin = min([p[0] for p in points])
            if shadeinclmax is None:
                shadeinclmax = max([p[0] for p in points])

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
            plot=self.ax.plot(x, y, 'b-')

            if shadeinclmin is not None and shadeinclmax is not None:
                if shadeinclmin < upper and shadeinclmax > lower:
                    x_shade = np.linspace(max(shadeinclmin, lower), min(shadeinclmax, upper), 100)
                    y_shade = a * x_shade ** 3 + b * x_shade ** 2 + c * x_shade + d
                    self.ax.fill_between(x_shade, y_shade, 0, color='yellow', alpha=0.3)


            if self.showcursors:
                x_vals=x
                cursor = mplcursors.cursor(plot, hover=True)
                cdf_vals = cdf_func(x_vals)
                @cursor.connect("add")
                def on_add(sel):
                    x, y = sel.target
                    index = np.argmin(np.abs(x_vals - x))
                    sel.annotation.set_text(f"x = {sel.target[0]:.2f}\nP(X<=x)={cdf_vals[index]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)

        self.ax.set_ylim(bottom=0)
        self.ax.autoscale_view()
        self.canvas.draw()

    def add_point_on_click(self, event):
        x_data = self.ax.get_xlim()[0] + (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * event.x / self.canvas.get_tk_widget().winfo_width()
        y_data = self.ax.get_ylim()[1] + (self.ax.get_ylim()[0] - self.ax.get_ylim()[1]) * event.y / self.canvas.get_tk_widget().winfo_height()
        y_data = max(0, y_data)
        self.add_point(point=(x_data, y_data))

class DistributionGraph(tk.Frame):
    def __init__(self, master, showcursors=False):
        super().__init__(master)
        self.showcursors = showcursors
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def update_plot(self, x_vals, y_vals,graph_type,cdf_vals,shadeinclmin=None,shadeinclmax=None):
        self.ax.clear()

        if shadeinclmin is not None or shadeinclmax is not None:
            if shadeinclmin is None:
                shadeinclmin = min(x_vals)
            if shadeinclmax is None:
                shadeinclmax = max(x_vals)

        if graph_type == 'bar':
            bars=self.ax.bar(x_vals, y_vals)
            if shadeinclmin is not None and shadeinclmax is not None:
                for bar, x in zip(bars, x_vals):
                    if shadeinclmin <= x <= shadeinclmax:
                        bar.set_color('orange')
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
            if shadeinclmin is not None and shadeinclmax is not None:
                mask = (x_vals >= shadeinclmin) & (x_vals <= shadeinclmax)
                self.ax.fill_between(x_vals[mask], 0, y_vals[mask], color='green', alpha=0.5)

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
    def __init__(self, master,parameters,on_change):
        super().__init__(master)
        self.grid_propagate(False)

        self.on_change = on_change

        for param in parameters.values():
            LabelSpinbox(self,param,self.on_change).pack()


class PiecewiseSettingsFrame(tk.Frame):
    def __init__(self, master,on_change,add,remove,normalise):
        super().__init__(master)
        self.grid_propagate(False)

        self.rbs=PairRadioButton(self,["Cubic Splines","Linear"],on_change)
        self.add_button = tk.Button(self,text="Add Point", command=add)
        self.remove_button = tk.Button(self, text="Remove Point", command=remove)
        self.normalise_button=tk.Button(self,text="Normalise",command=normalise)

        self.place_widgets()

    def place_widgets(self):
        self.rbs.grid(column=0, row=0)
        self.add_button.grid(column=0, row=1)
        self.remove_button.grid(column=0, row=2)
        self.normalise_button.grid(column=0, row=3)


class CalculationFrame(tk.Frame):
    def __init__(self, master, model,shadebetween):
        super().__init__(master)
        self.grid_propagate(False)
        self.model = model
        self.shadebetween = shadebetween

        self.l1 = tk.Label(self, text="P(X", width=2)
        self.cb = ttk.Combobox(self, values=["<", "≤"] + ["="] * (not (isinstance(self.model, Normal) or isinstance(self.model,Piecewise)) ) + ["≥", ">", "< <", "≤ ≤"],width=2)

        self.e1var=tk.StringVar()
        self.e2var=tk.StringVar()
        self.e3var=tk.StringVar()

        self.e1 = tk.Entry(self, width=6,textvariable=self.e1var)
        self.l2 = tk.Label(self, text=")=", width=2)
        self.e2 = tk.Entry(self, width=6,textvariable=self.e2var)

        self.l1a = tk.Label(self, text="P(", width=2)
        self.l1bvar = tk.StringVar(self)
        self.l1bvar.set("X")

        self.l1b = tk.Label(self, textvariable=self.l1bvar, width=2)
        self.e3 = tk.Entry(self, width=6,textvariable=self.e3var)

        self.e1.bind('<KeyRelease>', self.e1_updating)
        self.e2.bind('<KeyRelease>', self.e2_updating)
        self.e3.bind('<KeyRelease>', self.e3_updating)

        self.cb.bind("<<ComboboxSelected>>", self.refresh)

        self.place_widgets()

    def place_widgets(self):
        for widget in self.winfo_children():
            widget.pack_forget()
        if self.cb.get() not in ["< <","≤ ≤"]:
            self.l1.pack(side="left")
            self.cb.pack(side="left")
        else:
            self.l1a.pack(side="left")
            self.e3.pack(side="left")
            self.l1b.pack(side="left")
            self.cb.pack(side="left")

        self.e1.pack(side="left")
        self.l2.pack(side="left")
        self.e2.pack(side="left")

    def refresh(self, *args):
        self.l1bvar.set(str(self.cb.get())[0] + "X")
        self.e2.config(state="normal")
        if ((not isinstance(self.model, Normal)) and self.cb.get() in ["< <","≤ ≤"]) or self.cb.get() == "=":
            self.e2.config(state="disabled")
        self.place_widgets()
        self.update_shading()

    def e1_updating(self, *args):
        try:
            a = np.float64(self.e3var.get())
        except ValueError:
            a=0
        x = np.float64(self.e1var.get())
        b=x
        pdict={"<":self.model.pxlessthan(x),
               "≤":self.model.pxlessthanequalto(x),
               "=":self.model.pxequals(x),
               "≥":self.model.pxgreaterthanequalto(x),
               ">":self.model.pxgreaterthan(x),
               "< <":self.model.pxexclusivein(a,b),
               "≤ ≤":self.model.pxinclusivein(a, b),
               }
        self.e2var.set(f"{pdict[self.cb.get()]:.4f}")
        print(self.e2var.get())
        self.update_shading()

    def e2_updating(self, *args):
        p = np.float64(self.e2var.get())
        if self.cb.get() not in ["< <","≤ ≤"]:
            pdict={"<":self.model.xplessthan(p),
                   "≤":self.model.xplessthanequalto(p),
                   "≥":self.model.xpgreaterthanequalto(p),
                   ">":self.model.xpgreaterthan(p),
                   }
            self.e1var.set(f"{pdict[self.cb.get()]:.4f}")
        else:
            a,b=self.model.xpexclusivein(p)
            self.e1var.set(f"{b:.4f}")
            self.e3var.set(f"{a:.4f}")
        self.update_shading()

    def e3_updating(self, *args):
        a = np.float64(self.e3var.get())
        b = np.float64(self.e1var.get())
        pdict={"< <":self.model.pxexclusivein(a,b),
               "≤ ≤":self.model.pxinclusivein(a, b),
               }
        self.e2var.set(f"{pdict[self.cb.get()]:.4f}")
        self.update_shading()

    def update_shading(self):
        if self.model.is_discrete:
            boundsdict = {"<":{"shadeinclmax":np.float64(self.e1var.get())-1},
                          "≤":{"shadeinclmax":np.float64(self.e1var.get())},
                          "=":{"shadeinclmin":np.float64(self.e1var.get()),"shadeinclmax":np.float64(self.e1var.get())},
                          "≥":{"shadeinclmin":np.float64(self.e1var.get())},
                          ">":{"shadeinclmin":np.float64(self.e1var.get())+1}}
            if self.cb.get() in ["< <","≤ ≤"]:
                boundsdict={"< <":{"shadeinclmin":np.float64(self.e3var.get())+1,"shadeinclmax":np.float64(self.e1var.get())-1},
                            "≤ ≤":{"shadeinclmin":np.float64(self.e3var.get()),"shadeinclmax":np.float64(self.e1var.get())}
                            }
        else:
            boundsdict = {"<":{"shadeinclmax":np.float64(self.e1var.get())},
                          "≤":{"shadeinclmax":np.float64(self.e1var.get())},
                          "≥":{"shadeinclmin":np.float64(self.e1var.get())},
                          ">":{"shadeinclmin":np.float64(self.e1var.get())},}
            if self.cb.get() in ["< <","≤ ≤"]:
                boundsdict ={"< <":{"shadeinclmin":np.float64(self.e3var.get()),"shadeinclmax":np.float64(self.e1var.get())},
                             "≤ ≤":{"shadeinclmin":np.float64(self.e3var.get()),"shadeinclmax":np.float64(self.e1var.get())}
                             }
        self.shadebetween(boundsdict[self.cb.get()])



class ComboboxFrame(tk.Frame):
    def __init__(self, master, options, on_change):
        super().__init__(master)
        self.grid_propagate(False)

        self.on_change = on_change
        self.cb=ttk.Combobox(self,values=options)
        self.definition=tk.Label(self,)

        self.latex_image=None

        self.cb.bind('<<ComboboxSelected>>',self.callback)

        self.place_widgets()

    def place_widgets(self):
        self.cb.grid(row=0, column=0, pady=5,)
        self.definition.grid(row=1, column=0, pady=5,)
        self.grid_columnconfigure(0, weight=1)

    def callback(self, *args):
        self.on_change(self.cb.get())

    def cleardefinition(self):
        self.definition.config(image=None)
        self.place_widgets()


    def setdefinition(self,definition):
        self.cleardefinition()
        self.latex_image = latex_to_tk_image(definition)
        self.definition.config(image=self.latex_image)
        self.place_widgets()



if __name__ == '__main__':
    from project.Piecewise import Normal, Parameter,Binomial
    n=Parameter("n",1,999,1,10)
    p=Parameter("p",0,1,0.05,0.5)
    binom=Binomial({"n":n,"p":p})

    params={"mu":Parameter("mu",-999,999,1,0),"sigma":Parameter("sigma",-999,999,1,1)}
    norm=Normal(params)
    root = tk.Tk()
    def shbet(shadeinclmin=None,shadeinclmax=None):
        print(shadeinclmin,shadeinclmax)
    cframe=CalculationFrame(root,norm,shbet)
    cframe.grid(column=0, row=0)
    root.mainloop()

if __name__ == "__main__":
    quit()
    from Piecewise import Normal, Parameter, Binomial
    mu=Parameter("mu",-999,999,1,0)
    sigma=Parameter("sigma",-999,999,1,1)
    n=Parameter("n",1,999,1,10)
    p=Parameter("p",0,1,0.05,0.5)
    norm=Normal({"mu":mu,"sigma":sigma})
    binom=Binomial({"n":n,"p":p})
    root = tk.Tk()

    graph = DistributionGraph(root,"hi",showcursors=False)
    graph.update_plot(*norm.get_plot_data(),shadeinclmin=1)
    graph.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == '__main__':
    quit()
    from Piecewise import Parameter
    def cb(option=None):
        print("hello",option)
    def add():
        print("add")
    def remove():
        print("remove")
    root = tk.Tk()
    params={"mu":Parameter("mu",-999,999,1,0),"sigma":Parameter("sigma",-999,999,1,1)}

    settings=DistributionSettingsFrame(root,None,params,cb)
    #settings=PiecewiseSettingsFrame(root,None,cb,add,remove)
    settings.grid(column=0, row=0)
    root.mainloop()


