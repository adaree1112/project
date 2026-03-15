import tkinter as tk

from helperWidgets import TwoLabels
from widgets import ComboboxFrame, DistributionSettingsFrame, DistributionGraph, DicetributionGraph, \
    DicetributionSettingsFrame, DiceCanvas, ModeMenu, PiecewiseSettingsFrame, PiecewiseGraph, CalculationFrame


class View(tk.Frame):
    """
    A GUI class for displaying and interacting with statistical models and calculations.
    Attributes
    ----------
    controller : Controller
        The controller object that handles the logic for model calculations and view updates.
    graph : tk.Frame
        The frame displaying the graph.
    combobox : ComboboxFrame
        The frame containing the combobox for selecting distributions.
    settings : tk.Frame
        The frame displaying the settings for the selected model.
    dice_or_calc : tk.Frame
        The frame displaying either the dice simulation or the calculation results.
    e_and_var : tk.Frame
        The frame displaying the expectation and variance.
    """

    def __init__(self, master: tk.Tk, controller: 'Controller') -> None:
        """
        Initialises the View class with the given `master` (root) and `controller`.
        Parameters
        ----------
        master : tk.Tk
            The root window for the application.
        controller : Controller
        The controller object that handles the logic for model calculations.
        """
        super().__init__(master)

        self.controller = controller

        self.graph = None
        self.combobox = None
        self.settings = None
        self.e_and_var = None
        self.dice_or_calc = None

        self.set_up_blank_view()

        self.grid_config()
        self.place_widgets()

        self.create_menu(master)
        self.controller.initialise_view(self)

    def set_up_blank_view(self) -> None:
        """
        Initialises the frames for the view: graph, combobox, settings, expectation/variance, and dice/calc.

        This method prepares the basic layout of the view with the blank frames for each section
        """
        self.graph = tk.Frame(self, bg="black")
        self.combobox = ComboboxFrame(self, self.controller.set_distribution)
        self.settings = tk.Frame(self, bg="lightgray")
        self.e_and_var = tk.Frame(self, bg="dimgrey")
        self.dice_or_calc = tk.Frame(self, bg="darkgrey")

    def grid_config(self) -> None:
        """
        Configures the grid layout for the view's frames.

        This method defines how the rows and columns are weighted.
        """
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=6)
        self.grid_rowconfigure(3, weight=1)

    def place_widgets(self) -> None:
        """
        Places the various frames (widgets) on the grid layout.
        """
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10, 5), pady=10)
        self.combobox.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.e_and_var.grid(row=3, column=1, sticky="nsew", padx=(5, 10), pady=(5, 10))
        self.dice_or_calc.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def set_definition(self, latex: str) -> None:
        """
        Sets the LaTeX definition for the selected distribution.

        Updates the definition displayed in the ComboboxFrame.

        Parameters
        ----------
        latex : str
            The LaTeX definition for the selected distribution.
        """
        self.combobox.set_definition(latex)

    def set_options(self, options: list[str]) -> None:
        """
        Sets the available options for  selecting distributions in the ComboboxFrame.
        Parameters
        ----------
        options: list of str
            The available options for selecting distributions in the ComboboxFrame.
        Returns
        -------

        """
        self.combobox.set_options(options)
        self.place_widgets()

    def set_settings(self, mode: str, *args, **kwargs) -> None:
        """
        Sets the settings frame based on the selected mode.

        Parameters
        ----------
        mode:str
            The selected mode, which determines which settings to display.
        *args,*kwargs : optional
            Additional arguments passed straight to the settings frame constructor
        """
        self.settings.destroy()
        match mode:
            case "Dice":
                self.settings = DicetributionSettingsFrame(self, *args, **kwargs)
            case "Dist":
                self.settings = DistributionSettingsFrame(self, *args, **kwargs)
            case "Piece":
                self.settings = PiecewiseSettingsFrame(self, *args, **kwargs)
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def set_graph(self, mode: str, *args, **kwargs):
        """
        Sets the graph frame based on the selected mode.

        Parameters
        ----------
        mode:str
            The selected mode, which determines which graph to display.
        *args,*kwargs : optional
            Additional arguments passed straight to the graph frame constructor
        """
        self.graph.destroy()
        match mode:
            case "Dice":
                self.graph = DicetributionGraph(self)
            case "Dist":
                self.graph = DistributionGraph(self)
            case "Piece":
                self.graph = PiecewiseGraph(self, *args, **kwargs)
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10, 5), pady=10)

    def update_e_and_var(self, labels: list[str], values: list[float]) -> None:
        """
        Updates the Expectation and Variance labels and values

        Replaces current e_and_var frame with a new one
        Parameters
        ----------
        labels : list of str
            The labels for the expectation and variance (e.g., "E(X)", "Var(X)").
        values : list of float
            The calculated values for expectation and variance.
        """
        self.e_and_var.destroy()
        self.e_and_var = TwoLabels(self, labels, values)
        self.e_and_var.grid(row=3, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def update_graph(self, *args, **kwargs) -> None:
        """
        Updates the graph with new data and settings

        Parameters
        ----------
        *args,*kwargs : optional
            Additional arguments passed straight to the graph updater.
        """
        self.graph.update_plot(*args, **kwargs)

    def update_dice_or_calc(self, mode: str, *args) -> None:
        """
        Updates the dice frame or calculation frame based on the mode.

        Parameters
        ----------
        mode : str
            The selected mode, which determines which frame to display
            "dice" | "calc"
        *args : optional
            Additional arguments to pass to the dice or calculation frame.
        """
        self.dice_or_calc.destroy()
        match mode:
            case "dice":
                self.dice_or_calc = DiceCanvas(self, *args)
            case "calc":
                self.dice_or_calc = CalculationFrame(self, *args)
        self.dice_or_calc.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def refresh_calc(self) -> None:
        """
        Refreshes the calculation display.
        """
        self.dice_or_calc.refresh()

    def create_menu(self, master: tk.Tk) -> None:
        """
        Creates and sets up the menu for the application.

        Parameters
        ----------
        master : tk.Tk
            The root window for the application.
        """

        options = {"Dice": ["'Normal'", "Binomial", "Geometric"],
                   "Dist": ["Normal", "Binomial", "Exponential", "Poisson", "Geometric", "Chi Squared"],
                   "Piece": ["Piecewise"],
                   }
        mode_menu = ModeMenu(master, self.controller.mode, self.controller.set_mode)
        master.config(menu=mode_menu.menubar)
        self.set_options(options[self.controller.mode])
