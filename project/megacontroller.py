import tkinter as tk

from sympy.stats.drv_types import GeometricDistribution

from PiecewiseGraph import ComboboxFrame, PiecewiseSettingsFrame, PiecewiseGraph, CalculationFrame
from project.LabelSpinbox import TwoLabels
from project.Piecewise import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric, GeoDice, \
    NormDice, BinDice
from project.PiecewiseGraph import DistributionSettingsFrame, DistributionGraph, DicetributionGraph, \
    DicetributionSettingsFrame, DiceCanvas


class MegaController:
    def __init__(self, root):
        self.root = root

        self.model=None

        self.piecewise_type="Cubic Splines"

        self.shadedict={"shadeinclmin":None,"shadeinclmax":None}

        self.graph = tk.Frame(bg="black")
        self.cb = ComboboxFrame(self.root, ["Normal","Binomial","Exponential","Poisson","Geometric","Piecewise"],self.set_distribution)
        self.settings=tk.Frame(bg="lightgray")
        self.eandvar=tk.Frame(bg="dimgrey")
        self.calc=tk.Frame(bg="darkgrey")

        self.place_widgets()

    def set_distribution(self, dist_type):
        self.shadedict={}
        match dist_type:
            case "Normal":
                self.cb.setdefinition(r"$X \sim N(\mu, \sigma^2)$")
                params={"mu":Parameter("μ",-999,999,0.1,0),
                        "sigma":Parameter("σ",0.1,999,0.1,1)}
                self.model=Normal(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.graph=DistributionGraph(self.root)
                self.refresh()
            case "Binomial":
                self.cb.setdefinition(r"$X \sim B(n, p)$")
                params={"n":Parameter("n",1,999,1,10),
                        "p":Parameter("p",0,1,0.01,0.5)}
                self.model=Binomial(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.graph=DistributionGraph(self.root)
                self.refresh()
            case "Exponential":
                self.cb.setdefinition(r"$X \sim \text{Exp}(\lambda)$")
                params={"lambda":Parameter("λ",0,999,.1,5)}
                self.model=Exponential(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.graph=DistributionGraph(self.root)
                self.refresh()
            case "Poisson":
                self.cb.setdefinition(r"$X \sim \text{Poi}(\lambda)$")
                params={"lambda":Parameter("λ",0,999,.1,5)}
                self.model=Poisson(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.graph=DistributionGraph(self.root)
                self.refresh()

            case "Geometric":
                self.cb.setdefinition(r"$X \sim \text{Geo}(p)$")
                params={"p":Parameter("p",0,1,0.01,0.5)}
                self.model=Geometric(params)
                self.settings = DistributionSettingsFrame(self.root, params, self.refresh)
                self.graph=DistributionGraph(self.root)
                self.refresh()
            case "Piecewise":
                self.cb.cleardefinition()
                self.model=Piecewise([(1,1),(2,3),(3,2)])
                self.settings=PiecewiseSettingsFrame(self.root,self.set_piecewise_type,self.handle_add_point,self.handle_remove_point,self.handle_normalise)
                self.graph=PiecewiseGraph(self.root,self,self.handle_add_point)
                self.refresh()
        self.calc=CalculationFrame(self.root,self.model,self.shadebetween)
        self.refresh()

    def shadebetween(self,shadedict):
        print(shadedict)
        self.shadedict=shadedict
        self.refresh()

    def set_piecewise_type(self,piecewise_type="Cubic Splines"):
        self.piecewise_type=piecewise_type
        self.refresh()
        self.calc.e1_updating()

    def refresh(self,piecewise_type="Cubic Splines"):
        self.eandvar=TwoLabels(self.root,["E(X)","Var(X)"],[self.model.expectation(), self.model.variance()])
        if isinstance(self.model,Piecewise):
            points = self.model.get_points()
            self.model.calculate_pieces(linear=(self.piecewise_type=="Linear"))
            self.graph.update_plot(points, self.model.pieces,**self.shadedict,cdf_func=self.model.cdf)
        else:
            x_vals,y_vals,graph_type,cdf_func=self.model.get_plot_data()
            self.graph.update_plot(x_vals,y_vals,graph_type,cdf_func=cdf_func,**self.shadedict)
        self.place_widgets()

    def point_moved(self,old_x,old_y,new_x,new_y):
        self.model.update_point(old_x,old_y,new_x,new_y)
        self.refresh()
        self.calc.e1_updating()

    def handle_add_point(self,point=None):
        self.model.add_point(point=point)
        self.refresh()
        self.calc.e1_updating()

    def handle_remove_point(self):
        self.model.remove_point()
        self.refresh()
        self.calc.e1_updating()

    def handle_normalise(self):
        self.model.normalise()
        self.refresh()
        self.calc.e1_updating()

    def place_widgets(self):
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)
        self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
        self.eandvar.grid(row=2,column=1, sticky="nsew", padx=(5,10),pady=5)
        self.calc.grid(row=3, column=1, sticky="nsew", padx=(5,10),pady=(5,10))

        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=2)

class DiceController:
    def __init__(self, root):
        self.root = root

        self.model=None

        self.graph = tk.Frame(bg="black")
        self.cb = ComboboxFrame(self.root, ["'Normal'","Binomial","Geometric"],self.set_distribution)
        self.settings=tk.Frame(bg="lightgray")
        self.eandvar=tk.Frame(bg="dimgrey")
        self.dice=tk.Frame(bg="darkgrey")

        #self.success_vals=[6]
        self.show_real=False

        self.grid_config()
        self.place_widgets()

    def grid_config(self):
        self.root.grid_columnconfigure(0, weight=4)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(2, weight=6)
        self.root.grid_rowconfigure(3, weight=1)

    def place_widgets(self):
        self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)
        self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
        self.eandvar.grid(row=3,column=1, sticky="nsew", padx=(5,10),pady=5)
        self.dice.grid(row=2, column=1, sticky="nsew", padx=(5,10),pady=(5,10))


    def set_distribution(self,dist_type):
        match dist_type:
            case "Geometric":
                params={"num":Parameter("num trials",1,99999,1,1),}
                self.cb.setdefinition(r"$X \sim \text{Geo}(p)$")
                self.model=GeoDice(params)

            case "'Normal'":
                params={"n":Parameter("n",25,999,1,10),
                        "num":Parameter("num trials",1,99999,1,1),}
                self.cb.setdefinition(r"$\overline{X} \sim N\left(\mu, \frac{\sigma^2}{n}\right)$")
                self.model=NormDice(params,self.refresh)
            case "Binomial":
                self.cb.setdefinition(r"$X \sim B(n, p)$")
                params={"n":Parameter("n",1,999,1,10),
                        "num":Parameter("num trials",1,99999,1,1),}
                self.model= BinDice(params, self.refresh)

        self.settings = DicetributionSettingsFrame(self.root, params, self.refresh)
        self.graph = DicetributionGraph(self.root)
        self.refresh()

    def refresh(self,success_vals=None,show_real=None):
        if success_vals is not None:
            self.model.success_vals = success_vals

        if show_real is not None:
            self.show_real = show_real

        self.eandvar=TwoLabels(self.root,["E(X)","Var(X)"]+["real E(X)","real Var(X)"]*self.show_real,self.model.EandVar(self.show_real))

        self.model.add_dice_row(n=self.model.parameters["num"].value-self.model.get_n_dice_row())
        data=self.model.get_plot_data(self.show_real)
        self.graph.update_plot(*data)
        self.dice=DiceCanvas(self.root,self.model.get_dice_data())
        self.place_widgets()


if __name__ == '__main__':

    root = tk.Tk()
    root.geometry("900x600")

    # 2. Create the Controller, which creates and manages the View
    controller = DiceController(root)

    root.mainloop()