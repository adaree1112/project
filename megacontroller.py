import tkinter as tk

from LabelSpinbox import TwoLabels
from Piecewise import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric, GeoDice,NormDice, BinDice
from PiecewiseGraph import ComboboxFrame,DistributionSettingsFrame, DistributionGraph, DicetributionGraph,DicetributionSettingsFrame, DiceCanvas, ModeMenu,PiecewiseSettingsFrame, PiecewiseGraph, CalculationFrame


class MEGAController:
    """
    Controller to manage various distribution models, piecewise functions and dice simulations.

    Attributes
    ----------
    view : 'View'
        The View object that interacts with the user interface and updates it with calculated data.
    menubar : ModeMenu
        The menu bar object, used for switching modes.
    model : object
        The model object that holds the parameters and calculates values.
    mode : str
        The current mode of the controller.
        "Dis" | "Dice" | "Piece"
    piecewise_type : str
        The type of piecewise interpolation to use.
        "Cubic Splines" | "Linear"
    show_real : bool
        A flag indicating whether to overlay real values on the graph.
        Also dictates whether to show the real E(X) and Var(X)
    shade_dict : dict
        Dictionary that holds the minimum and maximum bounds for the shaded region
    """
    def __init__(self,view: None,starting_mode:str)->None:
        """
        Initialises the Controller with the given view.

        Parameters
        ----------
        view: 'View'
            The view object hich is used to interact with the UI.
        """
        self.view = view
        self.menubar = None
        self.mode=starting_mode

        self.piecewise_type="Cubic Splines"
        self.show_real=False
        self.model=None
        self.shade_dict={"shade_min":None, "shade_max":None}

    def set_distribution(self,dist_type:str)->None:
        """
        Sets the distribution model based on current mode and given distribution type.

        It updated the model and then updates the view with the relevant settings and graph.

        Parameters
        ----------
        dist_type:str
            The type of distribution model to set.
            "Normal" | "Binomial" | "Exponential"|"Poisson"|"Geometric"|"Piecewise"
            when dist_type = "Piecewise", dist_type is not used as that mode only has one type

        Returns
        -------

        """
        latex=""
        settings_args=[]
        settings_kwargs={}
        graph_args=[]
        match self.mode:
            case "Dis":
                match dist_type:
                    case "Normal":
                        latex = r"$X \sim N(\mu, \sigma^2)$"
                        params = {"mu": Parameter("μ", -999, 999, 0.1, 0),
                                  "sigma": Parameter("σ", 0.1, 999, 0.1, 1)}
                        self.model = Normal(params)
                        settings_args = [params, self.refresh]
                    case "Binomial":
                        latex = r"$X \sim B(n, p)$"
                        params = {"n": Parameter("n", 1, 999, 1, 10),
                                  "p": Parameter("p", 0, 1, 0.01, 0.5)}
                        self.model = Binomial(params)
                        settings_args = [params, self.refresh]
                    case "Exponential":
                        latex = r"$X \sim \text{Exp}(\lambda)$"
                        params = {"lambda": Parameter("λ", 0, 999, .1, 5)}
                        self.model = Exponential(params)
                        settings_args = [params, self.refresh]
                    case "Poisson":
                        latex = r"$X \sim \text{Poi}(\lambda)$"
                        params = {"lambda": Parameter("λ", 0, 999, .1, 5)}
                        self.model = Poisson(params)
                        settings_args = [params, self.refresh]
                    case "Geometric":
                        latex = r"$X \sim \text{Geo}(p)$"
                        params = {"p": Parameter("p", 0, 1, 0.01, 0.5)}
                        self.model = Geometric(params)
                        settings_args = [params, self.refresh]
            case "Dice":
                match dist_type:
                    case "Geometric":
                        params = {"num": Parameter("num trials", 1, 1000, 1, 1), }
                        latex = r"$X \sim \text{Geo}(p)$"
                        self.model = GeoDice(params)
                        settings_args = [params, self.refresh]
                    case "'Normal'":
                        params = {"n": Parameter("n", 25, 100, 1, 25),
                                  "num": Parameter("num trials", 1, 1000, 1, 1), }
                        latex = r"$\overline{X} \sim N\left(\mu, \frac{\sigma^2}{n}\right)$"
                        self.model = NormDice(params, self.refresh)
                        settings_args = [params, self.refresh]
                        settings_kwargs = {"success_vals_required": False}
                    case "Binomial":
                        latex = r"$X \sim B(n, p)$"
                        params = {"n": Parameter("n", 1, 100, 1, 10),
                                  "num": Parameter("num trials", 1, 1000, 1, 1), }
                        self.model = BinDice(params, self.refresh)
                        settings_args = [params, self.refresh]
            case "Piece":
                self.model = Piecewise([(1, 1), (2, 3), (3, 2)])
                settings_args = [self.set_piecewise_type, self.handle_add_point, self.handle_remove_point,self.handle_normalise]
                graph_args = [self, self.handle_add_point]

        if self.mode!="Dice":
            self.show_real = False
            self.view.update_dice_or_calc("calc", self.model, self.shade_between)

        self.view.set_definition(latex)
        self.view.set_settings(self.mode,*settings_args,**settings_kwargs)
        self.view.set_graph(self.mode,*graph_args)
        self.refresh()

    def shade_between(self, shade_dict:dict)->None:
        """
        Updates the shading bounds dictionary.

        It then refreshes to update the graph

        Parameters
        ----------
        shade_dict : dict
            A dictionary containing the shading information
        """
        self.shade_dict=shade_dict
        self.refresh()

    def refresh(self,success_vals:list[int]=None,show_real:bool=None)->None:
        """
        Refreshes the model and updates the view by updating E(X) and Var(X) data, and updating the graph

        Parameters
        ----------
        success_vals : list
            A list of success values to update the model with.
        show_real : bool
            A flag indicating whether to overlay real values on the graph
            Also indicates whether to show the real E(X) and Var(X)
        """
        if success_vals is not None:
            self.model.success_vals = success_vals
        if show_real is not None:
            self.show_real = show_real

        labels=["E(X)","Var(X)"]+["real E(X)","real Var(X)"]*self.show_real
        if self.mode=="Dice":
            values = self.model.e_and_var(self.show_real)
        else:
            values = [self.model.expectation(), self.model.variance()]
        self.view.update_e_and_var(labels, values)

        graph_args,graph_kwargs=[],{}
        match self.mode:
            case "Dice":
                self.model.add_dice_row(n=self.model.parameters["num"].value - self.model.get_n_dice_row())
                graph_args = self.model.get_plot_data(self.show_real)
                self.view.update_dice_or_calc("dice", self.model.get_dice_data())
            case "Dis":
                x_vals, y_vals, graph_type, cdf_func = self.model.get_plot_data()
                graph_args = [x_vals, y_vals, graph_type]
                graph_kwargs = {"cdf_func": cdf_func, **self.shade_dict}
            case "Piece":
                points = self.model.get_points()
                self.model.calculate_pieces(linear=(self.piecewise_type == "Linear"))
                graph_args = [points, self.model.pieces,self.model.is_normalised]
                graph_kwargs = {"cdf_func": self.model.cdf, **self.shade_dict}
        self.view.update_graph(*graph_args,**graph_kwargs)

    def initialise_view(self,view:'View')->None:
        """
        Create Link to View.

        Parameters
        ----------
        view : View
            The View object that will be used to interact with the view.
        """

        if self.view is None:
            self.view = view

    def set_mode(self,mode:str)->None:
        """
        Changes the mode of the controller and updates the options available in the view
        Parameters
        ----------
        mode:str
            The new mode
            "Dis" | "Dice" | Piece"
        """
        options={"Dice":["'Normal'", "Binomial", "Geometric"],
                 "Dis":["Normal", "Binomial", "Exponential", "Poisson", "Geometric"],
                 "Piece":["Piecewise"],
                 }
        self.mode = mode
        self.view.set_up_blank_view()
        self.view.set_options(options[self.mode])


    def set_piecewise_type(self, piecewise_type:str="Cubic Splines")->None:
        """
        Sets the type of piecewise function and refreshes the view.

        Parameters
        ----------
        piecewise_type : str
            The type of piecewise function
            "Linear" | "Cubic Splines"
        """
        self.piecewise_type = piecewise_type
        self.refresh()
        self.view.refresh_calc()

    def point_moved(self, old_x:float, old_y:float, new_x:float, new_y:float)->None:
        """
        Updates a point in the model with a new position and refreshes the view.

        Parameters
        ----------
        old_x:float
            The old x-coordinate
        old_y:float
            The old y-coordinate
        new_x:float
            The new x-coordinate
        new_y:float
            The new y-coordinate
        """
        self.model.update_point(old_x, old_y, new_x, new_y)
        self.refresh()
        self.view.refresh_calc()

    def handle_add_point(self, point:tuple[float,float]=None)->None:
        """
        Adds a new point to the model and refreshes the view.

        Parameters
        ----------
        point:tuple
            a tuple representing the (x,y) coordinates of the new point
        """
        self.model.add_point(point=point)
        self.refresh()
        self.view.refresh_calc()

    def handle_remove_point(self)->None:
        """
        Removes a point from the model and refreshes the view.
        """
        self.model.remove_point()
        self.refresh()
        self.view.refresh_calc()

    def handle_normalise(self)->None:
        """
        Normalises the model and refreshes the view.
        """
        self.model.normalise()
        self.refresh()
        self.view.refresh_calc()




class View(tk.Frame):
    """
    A GUI class for displaying and interacting with statistical models and calculations.
    Attributes
    ----------
    controller : MEGAController
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
    def __init__(self,master:tk.Tk,controller:MEGAController)->None:
        """
        Initialises the View class with the given `master` (root) and `controller`.
        Parameters
        ----------
        master : tk.Tk
            The root window for the application.
        controller : MEGAController
        The controller object that handles the logic for model calculations.
        """
        super().__init__(master)

        self.controller = controller

        self.graph=None
        self.combobox=None
        self.settings=None
        self.e_and_var=None
        self.dice_or_calc=None

        self.set_up_blank_view()


        self.grid_config()
        self.place_widgets()

        self.create_menu(master)
        self.controller.initialise_view(self)

    def set_up_blank_view(self)->None:
        """
        Initialises the frames for the view: graph, combobox, settings, expectation/variance, and dice/calc.

        This method prepares the basic layout of the view with the blank frames for each section
        """
        self.graph = tk.Frame(self,bg="black")
        self.combobox = ComboboxFrame(self, self.controller.set_distribution)
        self.settings=tk.Frame(self,bg="lightgray")
        self.e_and_var=tk.Frame(self, bg="dimgrey")
        self.dice_or_calc=tk.Frame(self, bg="darkgrey")

    def grid_config(self)->None:
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

    def place_widgets(self)->None:
        """
        Places the various frames (widgets) on the grid layout.
        """
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)
        self.combobox.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(10, 5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
        self.e_and_var.grid(row=3, column=1, sticky="nsew", padx=(5, 10), pady=(5, 10))
        self.dice_or_calc.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def set_definition(self, latex:str)->None:
        """
        Sets the LaTeX definition for the selected distribution.

        Updates the definition displayed in the ComboboxFrame.

        Parameters
        ----------
        latex : str
            The LaTeX definition for the selected distribution.
        """
        self.combobox.set_definition(latex)

    def set_options(self, options:list[str])->None:
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

    def set_settings(self,mode:str, *args,**kwargs)->None:
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
            case "Dis":
                self.settings = DistributionSettingsFrame(self, *args, **kwargs)
            case "Piece":
                self.settings = PiecewiseSettingsFrame(self, *args, **kwargs)
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)

    def set_graph(self, mode:str,*args,**kwargs):
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
                self.graph=DicetributionGraph(self)
            case "Dis":
                self.graph=DistributionGraph(self)
            case "Piece":
                self.graph=PiecewiseGraph(self,*args,**kwargs)
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)

    def update_e_and_var(self, labels:list[str], values:list[float])->None:
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
        self.e_and_var=TwoLabels(self, labels, values)
        self.e_and_var.grid(row=3, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def update_graph(self,*args,**kwargs)->None:
        """
        Updates the graph with new data and settings

        Parameters
        ----------
        *args,*kwargs : optional
            Additional arguments passed straight to the graph updator.
        """
        self.graph.update_plot(*args,**kwargs)


    def update_dice_or_calc(self,mode:str,*args)->None:
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
                self.dice_or_calc=DiceCanvas(self, *args)
            case "calc":
                self.dice_or_calc=CalculationFrame(self, *args)
        self.dice_or_calc.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)

    def refresh_calc(self)->None:
        """
        Refreshes the calculation display.
        """
        self.dice_or_calc.refresh()

    def create_menu(self, master:tk.Tk)->None:
        """
        Creates and sets up the menu for the application.

        Parameters
        ----------
        master : tk.Tk
            The root window for the application.
        """

        options={"Dice":["'Normal'", "Binomial", "Geometric"],
                 "Dis":["Normal", "Binomial", "Exponential", "Poisson", "Geometric"],
                 "Piece":["Piecewise"],
                 }
        mode_menu = ModeMenu(master, self.controller.mode, self.controller.set_mode)
        master.config(menu=mode_menu.menubar)
        self.set_options(options[self.controller.mode])


if __name__ == '__main__':

    the_root = tk.Tk()
    the_root.geometry("900x600")

    the_controller = MEGAController(None,"Dis")
    the_view = View(the_root, the_controller)
    the_view.pack(fill="both", expand=True)
    the_root.resizable(False,False)
    the_root.mainloop()