import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
from PIL import Image, ImageTk
import mplcursors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import ndarray

from Piecewise import Piecewise, AbstractStatisticalModel, Normal
from DraggablePoint import DraggablePoint
from LaTeXformulaimage import latex_to_tk_image
from LabelSpinbox import LabelSpinbox, PairRadioButton, DiceChoices


class PiecewiseGraph(tk.Frame):
    """
    A frame widget that displays a piecewise graph with draggable points

    Attributes
    ----------
    controller : object
        the controller responsible for handling the data and updates.
    add_point : callable
        A function that adds a point to the graph.
    fig : Figure
        The matplotlib figure for plotting.
    ax : Axes
        The matplotlib axes object where the graph is drawn.
    canvas : FigureCanvasTkAgg
        The canvas that integrates the matplotlib plot into tkinter.
    draggable_points : list of DraggablePoint
        A list of Draggable points on the graph.
    """
    def __init__(self, master:tk.Widget, controller:object,add_point:callable)->None:
        """
        Initialises the PiecewiseGraph frame.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        controller : object
            The controller responsible for handling the data and updates.
        add_point:callable
            A function that adds a point to the graph.
        """
        super().__init__(master)
        self.grid_propagate(False)

        self.controller = controller
        self.add_point = add_point

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.canvas.get_tk_widget().bind("<Double-Button-1>", self.add_point_on_click)

        self.draggable_points = []

    def update_plot(
            self,
            points:list[tuple[float|int|np.float64,float|int|np.float64]],
            pieces:list[ndarray],
            is_normalised:bool,
            cdf_func:callable=None,
            shade_min:int|float|np.float64=None,
            shade_max:int|float|np.float64=None,
            show_cursors:bool=True)->None:
        """
        Updates the plot based on new data, including shading.

        Parameters
        ----------
        points : list of tuple of float
            A list of points (x,y) to plot as red dots.
        pieces : list of ndarray
            A list of arrays representing cubic splines for each interval.
            Each array has the form [x1,x2,a,b,c,d].
            This represents the equation f(x) = a*x^3 + b*x^2 + c*x + d over the range [x1,x2]
        is_normalised : bool
            Whether the pieces and points are normalised.
            i.e. whether the pieces integrate to 1
        cdf_func : callable
            A CDF function to display when hovering over points
        shade_min : float
            The lower bound of the shaded region.
            Default is None
        shade_max : float
            The upper bound of the shaded region.
            Default is None
        show_cursors : bool
            Whether to show the cursors on the graph.
            Default is True
        """
        if shade_min is not None or shade_max is not None:
            if shade_min is None:
                shade_min = min([p[0] for p in points])
            if shade_max is None:
                shade_max = max([p[0] for p in points])

        self.ax.clear()
        self.draggable_points = []

        for coord in points:
            point = DraggablePoint(coord, self.controller)
            point.attach(self.ax)
            self.draggable_points.append(point)

        x, y = zip(*points)
        self.ax.plot(x, y, 'ro')

        x_vals=np.array([])
        y_vals=np.array([])

        for piece in pieces:
            lower, upper, a, b, c, d, = piece
            x = np.linspace(lower, upper, 50)
            y = a * x ** 3 + b * x ** 2 + c * x + d

            x_vals = np.concatenate((x_vals, x))
            y_vals = np.concatenate((y_vals, y))

            if shade_min is not None and shade_max is not None:
                if shade_min < upper and shade_max > lower:
                    x_shade = np.linspace(max(shade_min, lower), min(shade_max, upper), 100)
                    y_shade = a * x_shade ** 3 + b * x_shade ** 2 + c * x_shade + d
                    self.ax.fill_between(x_shade, y_shade, 0, color='yellow', alpha=0.3)

        plot=self.ax.plot(x_vals, y_vals, 'b-')

        if show_cursors and is_normalised:
            cursor = mplcursors.cursor(plot, hover=True)
            @cursor.connect("add")
            def on_add(sel):
                sel.annotation.set_text(f"x = {sel.target[0]:.2f}\nP(X<=x)={cdf_func(sel.target[0]):.4f}")
                sel.annotation.get_bbox_patch().set(alpha=0.8)

        self.ax.set_ylim(bottom=0)
        self.ax.autoscale_view()
        self.canvas.draw()

    def add_point_on_click(self, event:tk.Event)->None:
        """
        Adds a point to the graph when double-clicked.

        Parameters
        ----------
        event : tk.Event
            The mouse event triggered by the double click.
        """
        x_data = self.ax.get_xlim()[0] + (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * event.x / self.canvas.get_tk_widget().winfo_width()
        y_data = self.ax.get_ylim()[1] + (self.ax.get_ylim()[0] - self.ax.get_ylim()[1]) * event.y / self.canvas.get_tk_widget().winfo_height()
        y_data = max(0, y_data)
        self.add_point(point=(x_data, y_data))

class DistributionGraph(tk.Frame):
    """
    A frame widget that displays a distribution graph with different plot types.

    Attributes
    ----------
    fig : Figure
        The matplotlib figure for plotting.
    ax : Axes
        The matplotlib axes object where the graph is drawn.
    canvas : FigureCanvasTkAgg
        The canvas that integrates the matplotlib plot into tkinter.
    """
    def __init__(self, master:tk.Widget)->None:
        """
        Initialises the DistributionGraph frame.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        """
        super().__init__(master)
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def update_plot(self,
                    x_vals:list[float|np.float64]|np.ndarray[float|np.float64],
                    y_vals:list[float|np.float64]|np.ndarray[float|np.float64],
                    graph_type:str,
                    cdf_func:callable=None,
                    shade_min:int|float|np.float64 =None,
                    shade_max:int|float|np.float64=None,
                    show_cursors:bool=True)->None:
        """
        Updates the plot with new data.

        Supports bar and line graphs.

        Parameters
        ----------
        x_vals : list of floats
            The x-values of the data points.
        y_vals : list of floats
            The y-values of the data points.
        graph_type : str
            The type of graph to be drawn.
            "bar"|"line"
        cdf_func : callable
            A CDF function for hover details.
            Only required for line
        shade_min : float
            The lower bound of the shaded region.
            Default is None
        shade_max : float
            The upper bound of the shaded region.
            Default is None
        show_cursors : bool
            Whether to show the cursors on the graph.
            Default is True
        """
        self.ax.clear()

        if shade_min is not None or shade_max is not None:
            if shade_min is None:
                shade_min = min(x_vals)
            if shade_max is None:
                shade_max = max(x_vals)

        if graph_type == 'bar':
            bars=self.ax.bar(x_vals, y_vals)
            if shade_min is not None and shade_max is not None:
                for bar, x in zip(bars, x_vals):
                    if shade_min <= x <= shade_max:
                        bar.set_color('orange')
            if show_cursors:
                cursor = mplcursors.cursor(bars, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"x = {sel.target[0]:.0f}\nP(X=x)={sel.target[1]:.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)


        if graph_type == 'line':
            plot = self.ax.plot(x_vals, y_vals)
            self.ax.set_ylim(bottom=0)
            self.ax.set_xlim(right=max(x_vals), left=min(x_vals))
            if shade_min is not None and shade_max is not None:
                mask = (x_vals >= shade_min) & (x_vals <= shade_max)
                self.ax.fill_between(x_vals[mask], 0, y_vals[mask], color='green', alpha=0.5)

            if show_cursors:
                cursor = mplcursors.cursor(plot, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"x = {sel.target[0]:.2f}\nP(X≤x)={cdf_func(sel.target[0]):.4f}")
                    sel.annotation.get_bbox_patch().set(alpha=0.8)

        self.canvas.draw()

class DicetributionGraph(tk.Frame):
    """
    A frame widget that displays a die distribution graph comparing simulated and real data.

    Attributes
    ----------
    fig : Figure
        The matplotlib figure for plotting.
    ax : Axes
        The matplotlib axes object where the graph is drawn.
    canvas : FigureCanvasTkAgg
        The canvas that integrates the matplotlib plot into tkinter.
    """
    def __init__(self, master:tk.Widget)->None:
        """
        Initialises the DicetributionGraph frame.

        Parameters
        ----------
        master: tk.Widget
            The parent widget for the frame.
        """
        super().__init__(master)
        self.grid_propagate(False)

        self.fig = Figure(dpi=100)
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self,
                    x_vals:list[float|np.float64]|np.ndarray[float|np.float64],
                    y_vals:list[float|np.float64]|np.ndarray[float|np.float64],
                    r_x_vals:list[float|np.float64]|np.ndarray[float|np.float64]=None,
                    r_y_vals:list[float|np.float64]|np.ndarray[float|np.float64]=None,
                    r_graph_type:str=None):
        """
        Updates the plot with new simulated data and possibly real data.

        Can support bar and line graphs for real data
        Parameters
        ----------
        x_vals : list of floats
            The x-values of the data points.
        y_vals : list of floats
            The y-values of the data points.
        r_x_vals : list of floats
            The x-values of the real data points.
        r_y_vals : list of floats
            The y-values of the real data points.
        r_graph_type : str
            The type of graph to be drawn.
            "bar"|"line"
        """
        self.ax.clear()

        if r_x_vals is not None and r_graph_type == 'bar':
            bar_width = 0.35
            x_pos = range(len(x_vals))

            self.ax.bar([x - bar_width / 2 for x in x_pos], y_vals,width=bar_width, label='Simulated')
            self.ax.bar([x + bar_width / 2 for x in x_pos], r_y_vals,width=bar_width, color='orange', label='Real')

            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(x_vals)
            self.ax.legend()
        else:
            bar=self.ax.bar(x_vals, y_vals)

            if r_x_vals is not None and r_graph_type == 'line':
                bar.set_label("Simulated")
                self.ax.plot(r_x_vals, r_y_vals, color='orange', label='Real')
                self.ax.set_ylim(bottom=0)
                self.ax.set_xlim(right=6, left=0)

        self.canvas.draw()

class DicetributionSettingsFrame(tk.Frame):
    """
    A frame widget that manages dice distribution settings.

    Attributes
    ----------
    on_change : callable
        A callback function that is triggered when a setting changes.
    var : tk.BooleanVar
        A variable to store the state of the 'Show real' checkbox.
    check : ttk.checkbutton
        The checkbutton widget that toggles the 'show real' option.
    """
    def __init__(self, master:tk.Widget,parameters:dict[str,object],on_change:callable,success_vals_required:bool=True)->None:
        """
        Initialises  the dice distribution settings frame.

        Uses DiceChoices along with DistributionSettingsFrame.
        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        parameters : dict[str,object]
            A dictionary of parameters for configuring distribution settings
        on_change : callable
            A callback function that is triggered when a setting changes.
        success_vals_required : bool
            A flag to specify whether success vals are required.
            Default is True.
        """
        super().__init__(master)
        self.grid_propagate(False)

        self.on_change = on_change

        if success_vals_required:
            DiceChoices(self,on_change).pack()

        DistributionSettingsFrame(self,parameters,on_change).pack()
        self.var=tk.BooleanVar(value=False)
        self.check=ttk.Checkbutton(self,variable=self.var,command=self.on_button_change,text="Show real")
        self.check.pack()

    def on_button_change(self)->None:
        """
        Trigger the on_change callback when the 'Show real' checkbox is toggled.
        """
        self.on_change(show_real=self.var.get())

class DistributionSettingsFrame(tk.Frame):
    """
    a frame widget for managing the distribution settings with a set of parameter inputs.

    Attributes
    ----------
    on_change : callable
        A callback function that is triggered when a setting changes.
    """
    def __init__(self, master:tk.Widget,parameters:dict[str:object],on_change:callable)->None:
        """
        Initialises  the distribution settings frame with the given parameters.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        parameters : dict[str,object]
            A dictionary of parameters for configuring distribution settings
        on_change : callable
            A callback function that is triggered when a setting changes.
        """
        super().__init__(master)
        self.grid_propagate(False)

        self.on_change = on_change

        for param in parameters.values():
            LabelSpinbox(self,param,self.on_change).pack()


class PiecewiseSettingsFrame(tk.Frame):
    """
    A frame widget for managing the piecewise distribution settings.

    Attributes
    ----------
    radiobuttons : PairRadioButton
        The radio button widget for choosing piecewise type.
    add_button : tk.Button
        A button to add a new point to the piecewise function.
    remove_button : tk.Button
        A button to remove a point to the piecewise function.
    normalise_button : tk.Button
        A button to normalise the piecewise function.
    """
    def __init__(self, master:tk.Widget,on_change:callable,add:callable,remove:callable,normalise:callable)->None:
        """
        Initialises  the piecewise settings frame.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        on_change : callable
            A callback function that is triggered when the radiobuttons change.
        add : callable
            A callback function that is triggered when the add button is pressed.
        remove : callable
            A callback function that is triggered when the remove button is pressed.
        normalise : callable
            A callback function that is triggered when the normalise button is pressed.
        """
        super().__init__(master)
        self.grid_propagate(False)

        self.radiobuttons=PairRadioButton(self, ["Cubic Splines", "Linear"], on_change)
        self.add_button = tk.Button(self,text="Add Point", command=add)
        self.remove_button = tk.Button(self, text="Remove Point", command=remove)
        self.normalise_button=tk.Button(self,text="Normalise",command=normalise)
        self.place_widgets()

    def place_widgets(self)->None:
        """
        Place widgets in the frame using the pack geometry manager.

        This arranges the widgets in a vertical layout.
        """
        self.radiobuttons.pack(side="top")
        self.add_button.pack(side="top", expand=True, fill="x")
        self.remove_button.pack(side="top", expand=True, fill="x")
        self.normalise_button.pack(side="top", expand=True, fill="x")


class CalculationFrame(tk.Frame):
    """
    A Frame widget for managing the calculations.

    It provides an interface where the user inputs a probability condition and a corresponding value is calculated and returned.

    Attributes
    ----------
    model : AbstractStatisticalModel
        A probability model that performs the calculations.
    shade_between : callable
        A function that causes the shading on the graph to update.
    label1: tk.Label
        Label widget displaying the left side of the probability expression.
        "P(X"
    label1_a : tk.Label
        Label widget displaying the left side of the left side of the probability expression.
        "P("
    label1_b_var : tk.StringVar
        String var for part of label1_b containing an inequality sign
    label1_b : tk.Label
        Label widget displaying the right side of the left side of the probability expression.
        "<X"
    label2 : tk.Label
        Label widget displaying the right side of the probability expression.
        ")="
    entry1_var : tk.StringVar
        StringVar for the first entry widget.
        This is the variable that immediately follows the inequality, the 'x' in P(X<x)=p
    entry2_var : tk.StringVar
        StringVar for the second entry widget.
        This is the variable that immediately follows the equals sign, the 'p' in P(X<x)=p
    entry3_var : tk.StringVar
        StringVar for the third entry widget.
        This is the variable that immediately follows the open bracket, the 'a' in P(a<X<b)=p
    entry1 : tk.Entry
        This entry is the 'x' in P(X<x)=p
    entry2 : tk.Entry
        This entry is the 'p' in P(X<x)=p
    entry3 : tk.Entry
        This entry is the 'a' in P(a<X<b)=p
    combobox : ttk.Combobox
        Combobox widget allowing the user to select an (in)equality.
    """
    def __init__(self, master:tk.Widget, model:AbstractStatisticalModel, shade_between:callable)->None:
        """
        Initialises  the calculation frame with the given model and shading function.
        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        model : object
            The model that performs the calculations.
        shade_between : callable
            A function that causes the shading on the graph to update.
        """
        super().__init__(master)
        self.grid_propagate(False)
        self.model = model
        self.shade_between = shade_between

        self.label1 = tk.Label(self, text="P(X", width=2)
        self.combobox = ttk.Combobox(self, values=["<", "≤"] + ["="] * (not (isinstance(self.model, Normal) or isinstance(self.model, Piecewise))) + ["≥", ">", "< <", "≤ ≤"], width=2)

        self.entry1_var=tk.StringVar()
        self.entry2_var=tk.StringVar()
        self.entry3_var=tk.StringVar()

        self.entry1 = tk.Entry(self, width=6, textvariable=self.entry1_var)
        self.label2 = tk.Label(self, text=")=", width=2)
        self.entry2 = tk.Entry(self, width=6, textvariable=self.entry2_var)

        self.label1_a = tk.Label(self, text="P(", width=2)
        self.label1_b_var = tk.StringVar(self)
        self.label1_b_var.set("X")

        self.label1_b = tk.Label(self, textvariable=self.label1_b_var, width=2)
        self.entry3 = tk.Entry(self, width=6, textvariable=self.entry3_var)

        self.entry1.bind('<KeyRelease>', self.entry1_updating)
        self.entry2.bind('<KeyRelease>', self.entry2_updating)
        self.entry3.bind('<KeyRelease>', self.entry3_updating)

        self.combobox.bind("<<ComboboxSelected>>", self.refresh)

        self.place_widgets()

    def place_widgets(self) ->None:
        """
        Places all the widgets in the frame, updating their layout based on the current selection.

        Uses pack to place all widgets next to each other on the left
        """
        for widget in self.winfo_children():
            widget.pack_forget()
        if self.combobox.get() not in ["< <", "≤ ≤"]:
            self.label1.pack(side="left")
            self.combobox.pack(side="left")
        else:
            self.label1_a.pack(side="left")
            self.entry3.pack(side="left")
            self.label1_b.pack(side="left")
            self.combobox.pack(side="left")

        self.entry1.pack(side="left")
        self.label2.pack(side="left")
        self.entry2.pack(side="left")

    def refresh(self, _event:tk.Event=None)->None:
        """
        Refreshes the state of the widgets based on the current combobox selection.

        Updates the labels and entry widgets, and ensures that the correct fields are visible

        Parameters
        ----------
        _event : tk.Event
            Unused additional arguments for the event handler.
        """
        try:
            self.entry1_updating()
            self.label1_b_var.set(str(self.combobox.get())[0] + "X")
            self.entry2.config(state="normal")
            if ((not isinstance(self.model, Normal)) and self.combobox.get() in ["< <", "≤ ≤"]) or self.combobox.get() == "=":
                self.entry2.config(state="disabled")
            self.place_widgets()
            self.update_shading()
        except ValueError:
            pass

    def entry1_updating(self,_event:tk.Event=None)->None:
        """
        Updates the value of entry2 based on the current value of entry 1 (and 3) and combobox selection

        calculates probability and sets it in entry 2

        Parameters
        ----------
        _event : tk.Event
            Unused additional arguments for the event handler.
        """
        try:
            a = np.float64(self.entry3_var.get())
        except ValueError:
            a=0
        x = np.float64(self.entry1_var.get())
        b=x
        pdict={"<":self.model.pxlessthan(x),
               "≤":self.model.pxlessthanequalto(x),
               "=":self.model.pxequals(x),
               "≥":self.model.pxgreaterthanequalto(x),
               ">":self.model.pxgreaterthan(x),
               "< <":self.model.pxexclusivein(a,b),
               "≤ ≤":self.model.pxinclusivein(a, b),
               }
        self.entry2_var.set(f"{pdict[self.combobox.get()]:.4f}")
        self.update_shading()


    def entry2_updating(self, _event:tk.Event=None)->None:
        """
        Updates the value of entry1 (and 3) based on the current value of entry 2 and combobox selection

        Parameters
        ----------
        _event : tuple
            Unused additional arguments for the event handler.
        """
        p = np.float64(self.entry2_var.get())
        if self.combobox.get() not in ["< <", "≤ ≤"]:
            pdict={"<":self.model.xplessthan(p),
                   "≤":self.model.xplessthanequalto(p),
                   "≥":self.model.xpgreaterthanequalto(p),
                   ">":self.model.xpgreaterthan(p),
                   }
            self.entry1_var.set(f"{pdict[self.combobox.get()]:.4f}")
        else:
            a,b=self.model.xpexclusivein(p)
            self.entry1_var.set(f"{b:.4f}")
            self.entry3_var.set(f"{a:.4f}")
        self.update_shading()

    def entry3_updating(self, _event:tk.Event=None) -> None:
        """
        Updates the value of entry2 based on the current value of entry 1 and 3 and the combobox selection

        calculates probability and sets it in entry 2

        Parameters
        ----------
        _event : tuple
            Unused additional arguments for the event handler.
        """
        a = np.float64(self.entry3_var.get())
        b = np.float64(self.entry1_var.get())
        pdict={"< <":self.model.pxexclusivein(a,b),
               "≤ ≤":self.model.pxinclusivein(a, b),
               }
        self.entry2_var.set(f"{pdict[self.combobox.get()]:.4f}")
        self.update_shading()

    def update_shading(self)->None:
        """
        Updates the shading of the graph based on the current input values

        Adjusts the bounds dictionary depending on whether the model is discrete or continuous.
        """
        if self.model.is_discrete:
            bounds_dict = {"<":{"shade_max": np.float64(self.entry1_var.get()) - 1},
                          "≤":{"shade_max":np.float64(self.entry1_var.get())},
                          "=":{"shade_min":np.float64(self.entry1_var.get()), "shade_max":np.float64(self.entry1_var.get())},
                          "≥":{"shade_min":np.float64(self.entry1_var.get())},
                          ">":{"shade_min": np.float64(self.entry1_var.get()) + 1}}
            if self.combobox.get() in ["< <", "≤ ≤"]:
                bounds_dict={"< <":{"shade_min": np.float64(self.entry3_var.get()) + 1, "shade_max": np.float64(self.entry1_var.get()) - 1},
                            "≤ ≤":{"shade_min":np.float64(self.entry3_var.get()), "shade_max":np.float64(self.entry1_var.get())}
                            }
        else:
            bounds_dict = {"<":{"shade_max":np.float64(self.entry1_var.get())},
                          "≤":{"shade_max":np.float64(self.entry1_var.get())},
                          "≥":{"shade_min":np.float64(self.entry1_var.get())},
                          ">":{"shade_min":np.float64(self.entry1_var.get())}, }
            if self.combobox.get() in ["< <", "≤ ≤"]:
                bounds_dict ={"< <":{"shade_min":np.float64(self.entry3_var.get()), "shade_max":np.float64(self.entry1_var.get())},
                             "≤ ≤":{"shade_min":np.float64(self.entry3_var.get()), "shade_max":np.float64(self.entry1_var.get())}
                             }
        self.shade_between(bounds_dict[self.combobox.get()])



class ComboboxFrame(tk.Frame):
    """
    A frame widget that contains a combobox and a label displaying a definition

    Attributes
    ----------
    on_change : callable
        The callback function that is triggered when the combobox changes.
    combobox : ttk.Combobox
        The combobox widget containing the options.
    definition : tk.Label
        The label widget that displays the definition as an image
    latex_image : tk.PhotoImage
        The LaTeX image generated from the definition.
    """
    def __init__(self, master:tk.Widget, on_change:callable)->None:
        """
        Initialises the ComboboxFrame widget.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        on_change : callable
            The callback function that is triggered when the combobox changes.
        """
        super().__init__(master)
        self.grid_propagate(False)


        self.on_change = on_change
        self.combobox=ttk.Combobox(self, values=[])
        self.definition=tk.Label(self,)

        self.latex_image=None

        self.combobox.bind('<<ComboboxSelected>>', self.callback)

        self.place_widgets()

    def place_widgets(self)->None:
        """
        Places the combobox and definition label widgets within the frame.
        """
        self.combobox.pack(side="top", pady=5)
        self.definition.pack(side='top', pady=5,)

    def callback(self, _event:tk.Event=None)->None:
        """
        Callback function that is called when the combobox selection changes.

        Parameters
        ----------
        _event : tk.Event
            The arguments passed by the event, unused in this method.
        """
        self.on_change(self.combobox.get())

    def set_definition(self, definition:str)->None:
        """
        Sets the definition to be displayed in the label.

        Converts the LaTeX string into an image.

        Parameters
        ----------
        definition : str
            The LaTeX string to be displayed.
        """
        self.latex_image = latex_to_tk_image(definition)
        self.definition.config(image=self.latex_image)
        self.place_widgets()

    def set_options(self, options:list[str])->None:
        """
        Sets the options available in the combobox.

        Parameters
        ----------
        options : list[str]
            The list of options to be displayed.
        """
        self.combobox["values"]=options
        self.place_widgets()

dice_dict={}
size=(50,50)
def get_dice_image(number:int)->tk.PhotoImage:
    """
    Returns dice image for the specified number.

    If the image has already been generated, it will be returned from the dice_dict cache.
    If not, it loads, resizes and caches the image

    Parameters
    ----------
    number : int
        The number of the dice (1-6) for which the image is requested.

    Returns
    -------
    tk.PhotoImage
        The PhotoImage object representing the resized dice image.
    """
    if number not in dice_dict:
        image = Image.open(f'project/assets/dice/dice-{number}.png').resize(size, Image.Resampling.LANCZOS)
        dice_dict[number] = ImageTk.PhotoImage(image)
    return dice_dict[number]


class DiceRow(tk.Frame):
    """
    A frame that displays a row of dice images and an optional value label

    Attributes
    ----------
    dice_vals : list[int]
        A list of dice values to display as images
    row_val : float|int
        A value to display next to the images
        Default is None
    """
    def __init__(self, master:tk.Widget, dice_vals:list[int],row_val:float|int=None)->None:
        """
        Initialises the DiceRow widget.

        Parameters
        ----------
        master : tk.Widget
            The parent widget for the frame.
        dice_vals : list[int]
            A list of dice values to display as images
        row_val : float|int
            A value to display next to the images
        """
        super().__init__(master)
        self.dice_vals=dice_vals
        self.row_val=row_val
        self.create_row()

    def create_row(self)->None:
        """
        Creates the visual layout for the dice row and optional value label.
        """

        if not self.dice_vals:
            return

        for dice_val in self.dice_vals:
            tk.Label(self, image=get_dice_image(dice_val)).pack(side="left")

        if self.row_val is not None:
            separator = tk.Frame(self, width=2, bg="black")
            separator.pack(side="left", fill="y", padx=5)
            value_label = tk.Label(self, text=f"{self.row_val:.2f}", font=("Arial", 14))
            value_label.pack(side="left", padx=5)


class DiceCanvas(tk.Frame):
    """
    A canvas that contains a scrollable frame for displaying multiple DiceRow instances.

    Attributes
    ----------
    dice_vals_rows : list[tuple[list[int],int|float|None]]
        A list of tuples where each tuple consists of a list of dice and an optional value
    canvas : tk.Canvas
        The canvas widget used tp make the frame scrollable.
    y_scrollbar : tk.Scrollbar
        The canvas's vertical scrollbar
    x_scrollbar : tk.Scrollbar
        The canvas's horizontal scrollbar.
    scrollable_frame : tkk.Frame
        A frame inside the canvas that contains DiceRow instances.

    """
    def __init__(self, container_frame:tk.Frame, dice_vals_rows: list[tuple[list[int],int|float|None]])->None:
        """
        Initialises the DiceCanvas widget.

        Parameters
        ----------
        container_frame : tk.Frame
            The parent widget to which the canvas will be added.
        dice_vals_rows : list[tuple[list[int],int|float|None]]
            A list of tuples where each tuple consists of a list of dice and an optional value.
        """
        super().__init__(container_frame)
        self.grid_propagate(False)

        self.dice_vals_rows=dice_vals_rows
        self.canvas=tk.Canvas(self)
        self.y_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.x_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        self.place_widgets()

    def place_widgets(self)->None:
        """
        Places the canvas, scrollbars, and rows of dice within the parent widget.
        """
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        maxi=min(100,len(self.dice_vals_rows))
        if maxi<len(self.dice_vals_rows):
            tk.Label(self.scrollable_frame,text="only 100 are rendered due to processing power",font=("Arial", 10),fg="red").pack(side="top", anchor="nw")
        for dice_vals_row in self.dice_vals_rows[:maxi]:
            vals=dice_vals_row[0]
            num=dice_vals_row[1]
            DiceRow(self.scrollable_frame, vals,num).pack(side="top", anchor="nw")

class ModeMenu:
    """
    A menu for selecting and changing modes.

    Attributes
    ----------
    current_mode : str
        The currently selected mode.
    title_dict : dict
        A dictionary mapping mode identifiers to window titles.
    root : tk.Tk
        The root tkinter window
    callback : callable
        The callback function to be called when the mode is changed.
    menubar : tk.Menu
        The tkinter menubar widget for the application
    """
    def __init__(self, root:tk.Tk,mode:str,callback:callable)->None:
        """
        Initialises the ModeMenu widget.
        Parameters
        ----------
        root : tk.Tk
            The root tkinter window.
        mode : str
            The initial mode to set for the menu.
        callback : callable
            The callback function to be called when the mode is changed.
        """
        self.current_mode=mode
        self.title_dict={"Dis":"Distribution Calculation",
                         "Dice":"Dice Simulation",
                         "Piece":"Piecewise Distribution"}

        self.root = root
        self.root.title(self.title_dict[mode])
        self.callback = callback
        self.menubar = tk.Menu(root)
        self.create_mode_menu()
        self.create_help_menu()
        self.root.configure(menu=self.menubar)

    def create_mode_menu(self)->None:
        """
        Create the mode menu and add required commands to the menubar.
        """
        mode_menu = tk.Menu(self.menubar, tearoff=0)
        mode_menu.add_command(label="Distribution Calculation", command=lambda: self.mode_callback("Dis"))
        mode_menu.add_command(label="Dice Simulation", command=lambda: self.mode_callback("Dice"))
        mode_menu.add_command(label="Piecewise Distribution", command=lambda: self.mode_callback("Piece"))
        mode_menu.add_separator()
        mode_menu.add_command(label="", command=lambda: self.mode_callback("WOAH"))
        self.menubar.add_cascade(label="Mode", menu=mode_menu)

    def create_help_menu(self)->None:
        """
        Create the help menu and add required commands to the menubar.
        """
        help_menu = tk.Menu(self.menubar, tearoff=0)

        distribution_menu=tk.Menu(help_menu, tearoff=0)
        distribution_menu.add_command(label="Normal", command=lambda: self.help_callback("Dis","Normal"))
        distribution_menu.add_command(label="Geometric", command=lambda: self.help_callback("Dis","Geometric"))
        distribution_menu.add_command(label="Binomial", command=lambda: self.help_callback("Dis","Binomial"))
        distribution_menu.add_command(label="Exponential",command=lambda: self.help_callback("Dis","Exponential"))
        distribution_menu.add_command(label="Poisson",command=lambda: self.help_callback("Dis","Poisson"))
        help_menu.add_cascade(label="Distribution Calculation", menu=distribution_menu)

        dice_menu=tk.Menu(help_menu, tearoff=0)
        dice_menu.add_command(label="'Normal'", command=lambda: self.help_callback("Dice","'Normal'"))
        dice_menu.add_command(label="Geometric", command=lambda: self.help_callback("Dice","Geometric"))
        dice_menu.add_command(label="'Binomial'", command=lambda: self.help_callback("Dice","Binomial"))
        help_menu.add_cascade(label="Dice Simulation", menu=dice_menu)

        piecewise_menu=tk.Menu(help_menu, tearoff=0)
        piecewise_menu.add_command(label="Piecewise", command=lambda: self.help_callback("Piece","Piecewise"))
        help_menu.add_cascade(label="Piecewise Distribution", menu=piecewise_menu)

        self.menubar.add_cascade(label="HELP", menu=help_menu)

    def help_callback(self,mode:str,dist_type:str)->None:
        """
        Callback function that creates and opens a new help window.

        Parameters
        ----------
        mode : str
            The mode to help with.
        dist_type : str
            The distribution type to help with.
        """
        help_window = HelpWindow(self.root,f"help_{mode}_{dist_type}")
        help_window.title(f"Help for {self.title_dict[mode]}, {dist_type}")
        help_window.geometry("600x400")
        help_window.resizable(False,False)

    def mode_callback(self, mode:str)->None:
        """
        Callback function that changes the current mode and updates the window title.

        Parameters
        ----------
        mode : str
            The new mode to set
        """
        if mode!=self.current_mode:
            self.current_mode=mode
            self.root.title(self.title_dict[mode])
            self.callback(mode)

class HelpWindow(tk.Toplevel):
    """
    A pop-up window that displays scrollable text.

    The text will be help documentation for each mode

    Attributes
    ----------
    canvas : tk.Canvas
        The canvas widget used tp make the frame scrollable.
    y_scrollbar : tk.Scrollbar
        The canvas's vertical scrollbar
    x_scrollbar : tk.Scrollbar
        The canvas's horizontal scrollbar.
    scrollable_frame : tkk.Frame
        A frame inside the canvas that contains DiceRow instances.
    label : tk.Label
        The label that displays the provided text.
    """

    def __init__(self, root:tk.Tk, help_file_name:str)->None:
        """
        Initialises a new HelpWindow.

        Parameters
        ----------
        root : tk.Tk
            The parent root window to attach this window to.
        help_file_name : str
            The file name of the text to be displayed.
        """
        super().__init__(root)
        self.grid_propagate(False)

        self.canvas=tk.Canvas(self)
        self.y_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.x_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.help_file_name=help_file_name
        self.label = tk.Label(self.scrollable_frame, text=self.get_help_text(),font=("Courier", 10), justify="left", anchor="nw")

        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        self.place_widgets()

    def place_widgets(self)->None:
        """
        Places the canvas, scrollbars, and text within the new window using a grid layout.
        """
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label.pack(side="top", anchor="nw",fill="both", expand=True)

    def get_help_text(self)->str:
        """
        Gets the help text for the desired help window.

        Returns
        -------
        str
            the help text for the desired help window.
        """
        with open(f"project/assets/help/{self.help_file_name}.txt","r",encoding="utf-8") as file:
            return file.read()

if __name__ == "__main__":
    the_root = tk.Tk()
    the_root.geometry("900x600")

    text="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """

    the_help_window = HelpWindow(the_root, text)
    the_help_window.title("Help for, ")
    the_help_window.geometry("600x400")
    the_help_window.resizable(True, False)

    the_root.mainloop()

