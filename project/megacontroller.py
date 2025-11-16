import tkinter as tk

from PiecewiseGraph import ComboboxFrame, PiecewiseSettingsFrame
from project.Piecewise import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric
from project.PiecewiseGraph import DistributionSettingsFrame


class MegaController:
    def __init__(self, root):
        self.root = root

        self.model=None


        self.graph = tk.Label(bg="black")
        self.cb = ComboboxFrame(self.root, ["Normal","Binomial","Exponential","Poisson","Geometric","Piecewise"],self.set_distribution)
        self.settings=tk.Label(bg="lightgray")
        self.calc=tk.Label(bg="darkgrey")

        self.place_widgets()

    def set_distribution(self, dist_type):
        match dist_type:
            case "Normal":
                self.cb.setdefinition(r"$X \sim N(\mu, \sigma^2)$")
                params={"mu":Parameter("μ",-999,999,0.1,0),
                        "sigma":Parameter("σ",0.1,999,0.1,1)}
                self.model=Normal(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.place_widgets()
            case "Binomial":
                self.cb.setdefinition(r"$X \sim B(n, p)$")
                params={"n":Parameter("n",1,999,1,10),
                        "p":Parameter("p",0,1,0.01,0.5)}
                self.model=Binomial(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.place_widgets()
            case "Exponential":
                self.cb.setdefinition(r"$X \sim \text{Exp}(\lambda)$")
                params={"lambda":Parameter("λ",0,999,.1,5)}
                self.model=Exponential(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.place_widgets()
            case "Poisson":
                self.cb.setdefinition(r"$X \sim \text{Poi}(\lambda)$")
                params={"lambda":Parameter("λ",0,999,.1,5)}
                self.model=Poisson(params)
                self.settings=DistributionSettingsFrame(self.root,params,self.refresh)
                self.place_widgets()

            case "Geometric":
                self.cb.setdefinition(r"$X \sim \text{Geo}(p)$")
                params={"p":Parameter("p",0,1,0.01,0.5)}
                self.model=Geometric(params)
                self.settings = DistributionSettingsFrame(self.root, params, self.refresh)
                self.place_widgets()
            case "Piecewise":
                self.cb.cleardefinition()
                self.model=Piecewise([(1,1),(2,3),(3,2)])
                self.settings=PiecewiseSettingsFrame(self.root,self.refresh,self.model.add_point,self.model.remove_point)
                self.place_widgets()
    def refresh(self,*args):
        print("hello")


    def place_widgets(self):
        self.graph.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(10,5), pady=10)
        self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
        self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
        self.calc.grid(row=2, column=1, sticky="nsew", padx=(5,10),pady=(5,10))

        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=2)







if __name__ == '__main__':

    root = tk.Tk()
    root.geometry("900x600")

    # 2. Create the Controller, which creates and manages the View
    controller = MegaController(root)

    root.mainloop()