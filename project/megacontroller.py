import tkinter as tk

from PiecewiseGraph import ComboboxFrame, PiecewiseSettingsFrame, PiecewiseGraph, CalculationFrame
from project.LabelSpinbox import TwoLabels
from project.Piecewise import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric
from project.PiecewiseGraph import DistributionSettingsFrame, DistributionGraph


class MegaController:
    def __init__(self, root):
        self.root = root

        self.model=None

        self.piecewise_type="Cubic Splines"

        self.shadedict={"shadeinclmin":None,"shadeinclmax":None}

        self.graph = tk.Label(bg="black")
        self.cb = ComboboxFrame(self.root, ["Normal","Binomial","Exponential","Poisson","Geometric","Piecewise"],self.set_distribution)
        self.settings=tk.Label(bg="lightgray")
        self.eandvar=tk.Label(bg="dimgrey")
        self.calc=tk.Label(bg="darkgrey")

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
            x_vals,y_vals,graph_type,cdf_vals=self.model.get_plot_data()
            self.graph.update_plot(x_vals,y_vals,graph_type,cdf_vals,**self.shadedict)
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

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=2)







if __name__ == '__main__':

    root = tk.Tk()
    root.geometry("900x600")

    # 2. Create the Controller, which creates and manages the View
    controller = MegaController(root)

    root.mainloop()