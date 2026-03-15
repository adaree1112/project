from models import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric, GeoDice, NormDice, \
    BinDice, ChiSquared
from view import View


class Controller:
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
        "Dist" | "Dice" | "Piece"
    piecewise_type : str
        The type of piecewise interpolation to use.
        "Cubic Splines" | "Linear"
    show_real : bool
        A flag indicating whether to overlay real values on the graph.
        Also dictates whether to show the real E(X) and Var(X)
    shade_dict : dict
        Dictionary that holds the minimum and maximum bounds for the shaded region
    """

    def __init__(self, view: None, starting_mode: str) -> None:
        """
        Initialises the Controller with the given view.

        Parameters
        ----------
        view: 'View'
            The view object which is used to interact with the UI.
        """
        self.view = view
        self.mode = starting_mode
        self._is_refreshing = False
        self.piecewise_type = "Cubic Splines"
        self.show_real = False
        self.model = None
        self.shade_dict = {"shade_min": None, "shade_max": None}

    def set_distribution(self, dist_type: str) -> None:
        """
        Sets the distribution model based on current mode and given distribution type.

        It updated the model and then updates the view with the relevant settings and graph.

        Parameters
        ----------
        dist_type:str
            The type of distribution model to set.
            "Normal" | "Binomial" | "Exponential"|"Poisson"|"Geometric"|"Piecewise"
            when dist_type = "Piecewise", dist_type is not used as that mode only has one type

        """
        self.show_real = False
        latex = ""
        settings_args = []
        settings_kwargs = {}
        graph_args = []
        self.shade_dict = {"shade_min": None, "shade_max": None}
        match self.mode:
            case "Dist":
                params = {}
                match dist_type:
                    case "Normal":
                        latex = r"$X \sim N(\mu, \sigma^2)$"
                        params = {"mu": Parameter("μ", -999, 999, 0.1, 0),
                                  "sigma": Parameter("σ", 0.1, 999, 0.1, 1)}
                        self.model = Normal(params)
                    case "Binomial":
                        latex = r"$X \sim B(n, p)$"
                        params = {"n": Parameter("n", 1, 999, 1, 10),
                                  "p": Parameter("p", 0, 1, 0.01, 0.5)}
                        self.model = Binomial(params)
                    case "Exponential":
                        latex = r"$X \sim \text{Exp}(\lambda)$"
                        params = {"lambda": Parameter("λ", 0, 999, .1, 5)}
                        self.model = Exponential(params)
                    case "Poisson":
                        latex = r"$X \sim \text{Poi}(\lambda)$"
                        params = {"lambda": Parameter("λ", 0, 999, .1, 5)}
                        self.model = Poisson(params)
                    case "Geometric":
                        latex = r"$X \sim \text{Geo}(p)$"
                        params = {"p": Parameter("p", 0, 1, 0.01, 0.5)}
                        self.model = Geometric(params)
                    case "Chi Squared":
                        latex = r"$\chi_\nu^2 \sim Z_1^2 +...+ Z_\nu^2$" + "\n" + r"$Z \sim \text{N}(0,1)$"  # "$X \sim \chi_\nu^2$"
                        params = {"nu": Parameter("𝜈", 1, 99, 1, 1)}
                        self.model = ChiSquared(params)
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
                settings_args = [self.set_piecewise_type, self.handle_add_point, self.handle_remove_point,
                                 self.handle_normalise]
                graph_args = [self, self.handle_add_point]

        if self.mode != "Dice":
            self.show_real = False
            self.view.update_dice_or_calc("calc", self.model, self.shade_between)

        self.view.set_definition(latex)
        self.view.set_settings(self.mode, *settings_args, **settings_kwargs)
        self.view.set_graph(self.mode, *graph_args)
        self.refresh()

    def shade_between(self, shade_dict: dict) -> None:
        """
        Updates the shading bounds dictionary.

        It then refreshes to update the graph

        Parameters
        ----------
        shade_dict : dict
            A dictionary containing the shading information
        """
        self.shade_dict = shade_dict
        self.refresh()

    def refresh(self, success_vals: list[int] = None, show_real: bool = None) -> None:
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
        if self._is_refreshing:
            return

        self._is_refreshing = True
        if success_vals is not None:
            self.model.success_vals = success_vals
        if show_real is not None:
            self.show_real = show_real

        labels = ["E(X)", "Var(X)"] + ["real E(X)", "real Var(X)"] * self.show_real
        if self.mode == "Dice":
            values = self.model.e_and_var(self.show_real)
        else:
            values = [self.model.expectation(), self.model.variance()]
        self.view.update_e_and_var(labels, values)

        graph_args, graph_kwargs = [], {}
        match self.mode:
            case "Dice":
                self.model.add_dice_row(n=self.model.parameters["num"].value - self.model.get_n_dice_row())
                graph_args = self.model.get_plot_data(self.show_real)
                self.view.update_dice_or_calc("dice", self.model.get_dice_data())
            case "Dist":
                x_vals, y_vals, graph_type, cdf_func = self.model.get_plot_data()
                graph_args = [x_vals, y_vals, graph_type]
                graph_kwargs = {"cdf_func": cdf_func, **self.shade_dict}
                self.view.refresh_calc()
            case "Piece":
                points = self.model.get_points()
                self.model.calculate_pieces(linear=(self.piecewise_type == "Linear"))
                graph_args = [points, self.model.pieces, self.model.is_normalised]
                graph_kwargs = {"cdf_func": self.model.cdf, **self.shade_dict}
        self.view.update_graph(*graph_args, **graph_kwargs)
        self._is_refreshing = False

    def initialise_view(self, view: 'View') -> None:
        """
        Create Link to View.

        Parameters
        ----------
        view : View
            The View object that will be used to interact with the view.
        """

        if self.view is None:
            self.view = view

    def set_mode(self, mode: str) -> None:
        """
        Changes the mode of the controller and updates the options available in the view
        Parameters
        ----------
        mode:str
            The new mode
            "Dist" | "Dice" | "Piece"
        """
        options = {"Dice": ["'Normal'", "Binomial", "Geometric"],
                   "Dist": ["Normal", "Binomial", "Exponential", "Poisson", "Geometric", "Chi Squared"],
                   "Piece": ["Piecewise"],
                   }
        self.mode = mode
        self.view.set_up_blank_view()
        self.view.set_options(options[self.mode])

    def set_piecewise_type(self, piecewise_type: str = "Cubic Splines") -> None:
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

    def point_moved(self, old_x: float, old_y: float, new_x: float, new_y: float) -> None:
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

    def handle_add_point(self, point: tuple[float, float] = None) -> None:
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

    def handle_remove_point(self) -> None:
        """
        Removes a point from the model and refreshes the view.
        """
        self.model.remove_point()
        self.refresh()
        self.view.refresh_calc()

    def handle_normalise(self) -> None:
        """
        Normalises the model and refreshes the view.
        """
        self.model.normalise()
        self.refresh()
        self.view.refresh_calc()


if __name__ == '__main__':
    import tkinter as tk

    the_root = tk.Tk()
    the_root.geometry("900x600")
    # noinspection PyTypeChecker
    the_controller = Controller(None, "Dist")
    the_view = View(the_root, the_controller)
    the_view.pack(fill="both", expand=True)
    the_root.resizable(False, False)
    the_root.mainloop()
