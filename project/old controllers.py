# import tkinter as tk
#
# from PiecewiseGraph import ComboboxFrame, PiecewiseSettingsFrame, PiecewiseGraph, CalculationFrame
# from LabelSpinbox import TwoLabels
# from Piecewise import Parameter, Piecewise, Normal, Binomial, Exponential, Poisson, Geometric, GeoDice, \
#     NormDice, BinDice
# from PiecewiseGraph import DistributionSettingsFrame, DistributionGraph, DicetributionGraph, \
#     DicetributionSettingsFrame, DiceCanvas, ModeMenu
#
#
# # class MegaController(tk.Frame):
# #     def __init__(self, master):
# #         super().__init__(master)
# #
# #         self.model=None
# #
# #         self.piecewise_type="Cubic Splines"
# #
# #         self.shadedict={"shadeinclmin":None,"shadeinclmax":None}
# #
# #         self.graph = tk.Frame(self,bg="black")
# #         self.cb = ComboboxFrame(self, ["Normal","Binomial","Exponential","Poisson","Geometric","Piecewise"],self.set_distribution)
# #         self.settings=tk.Frame(self,bg="lightgray")
# #         self.eandvar=tk.Frame(self,bg="dimgrey")
# #         self.calc=tk.Frame(self,bg="darkgrey")
# #
# #         self.place_widgets()
# #
# #     def set_distribution(self, dist_type):
# #         self.shadedict={}
# #         match dist_type:
# #             case "Normal":
# #                 self.cb.setdefinition(r"$X \sim N(\mu, \sigma^2)$")
# #                 params={"mu":Parameter("μ",-999,999,0.1,0),
# #                         "sigma":Parameter("σ",0.1,999,0.1,1)}
# #                 self.model=Normal(params)
# #                 self.settings=DistributionSettingsFrame(self,params,self.refresh)
# #                 self.graph=DistributionGraph(self)
# #                 self.refresh()
# #             case "Binomial":
# #                 self.cb.setdefinition(r"$X \sim B(n, p)$")
# #                 params={"n":Parameter("n",1,999,1,10),
# #                         "p":Parameter("p",0,1,0.01,0.5)}
# #                 self.model=Binomial(params)
# #                 self.settings=DistributionSettingsFrame(self,params,self.refresh)
# #                 self.graph=DistributionGraph(self)
# #                 self.refresh()
# #             case "Exponential":
# #                 self.cb.setdefinition(r"$X \sim \text{Exp}(\lambda)$")
# #                 params={"lambda":Parameter("λ",0,999,.1,5)}
# #                 self.model=Exponential(params)
# #                 self.settings=DistributionSettingsFrame(self,params,self.refresh)
# #                 self.graph=DistributionGraph(self)
# #                 self.refresh()
# #             case "Poisson":
# #                 self.cb.setdefinition(r"$X \sim \text{Poi}(\lambda)$")
# #                 params={"lambda":Parameter("λ",0,999,.1,5)}
# #                 self.model=Poisson(params)
# #                 self.settings=DistributionSettingsFrame(self,params,self.refresh)
# #                 self.graph=DistributionGraph(self)
# #                 self.refresh()
# #
# #             case "Geometric":
# #                 self.cb.setdefinition(r"$X \sim \text{Geo}(p)$")
# #                 params={"p":Parameter("p",0,1,0.01,0.5)}
# #                 self.model=Geometric(params)
# #                 self.settings = DistributionSettingsFrame(self, params, self.refresh)
# #                 self.graph=DistributionGraph(self)
# #                 self.refresh()
# #             case "Piecewise":
# #                 self.cb.cleardefinition()
# #                 self.model=Piecewise([(1,1),(2,3),(3,2)])
# #                 self.settings=PiecewiseSettingsFrame(self,self.set_piecewise_type,self.handle_add_point,self.handle_remove_point,self.handle_normalise)
# #                 self.graph=PiecewiseGraph(self,self,self.handle_add_point)
# #                 self.refresh()
# #         self.calc=CalculationFrame(self,self.model,self.shadebetween)
# #         self.refresh()
# #
# #     def shadebetween(self,shadedict):
# #         self.shadedict=shadedict
# #         self.refresh()
# #
# #     def set_piecewise_type(self,piecewise_type="Cubic Splines"):
# #         self.piecewise_type=piecewise_type
# #         self.refresh()
# #         self.calc.e1_updating()
# #
# #     def refresh(self,piecewise_type="Cubic Splines"):
# #         self.eandvar=TwoLabels(self,["E(X)","Var(X)"],[self.model.expectation(), self.model.variance()])
# #         if isinstance(self.model,Piecewise):
# #             points = self.model.get_points()
# #             self.model.calculate_pieces(linear=(self.piecewise_type=="Linear"))
# #             self.graph.update_plot(points, self.model.pieces,**self.shadedict,cdf_func=self.model.cdf)
# #         else:
# #             x_vals,y_vals,graph_type,cdf_func=self.model.get_plot_data()
# #             self.graph.update_plot(x_vals,y_vals,graph_type,cdf_func=cdf_func,**self.shadedict)
# #         self.place_widgets()
# #
# #     def point_moved(self,old_x,old_y,new_x,new_y):
# #         self.model.update_point(old_x,old_y,new_x,new_y)
# #         self.refresh()
# #         self.calc.e1_updating()
# #
# #     def handle_add_point(self,point=None):
# #         self.model.add_point(point=point)
# #         self.refresh()
# #         self.calc.e1_updating()
# #
# #     def handle_remove_point(self):
# #         self.model.remove_point()
# #         self.refresh()
# #         self.calc.e1_updating()
# #
# #     def handle_normalise(self):
# #         self.model.normalise()
# #         self.refresh()
# #         self.calc.e1_updating()
# #
# #     def place_widgets(self):
# #         self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)
# #         self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
# #         self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
# #         self.eandvar.grid(row=2,column=1, sticky="nsew", padx=(5,10),pady=5)
# #         self.calc.grid(row=3, column=1, sticky="nsew", padx=(5,10),pady=(5,10))
# #
# #         self.grid_columnconfigure(0, weight=2)
# #         self.grid_columnconfigure(1, weight=1)
# #
# #         self.grid_rowconfigure(0, weight=2)
# #         self.grid_rowconfigure(1, weight=2)
# #         self.grid_rowconfigure(2, weight=1)
# #         self.grid_rowconfigure(3, weight=2)
#
# # class DiceController (tk.Frame):
# #     def __init__(self, master):
# #         super().__init__(master)
# #
# #         self.model=None
# #
# #         self.graph = tk.Frame(self,bg="black")
# #         self.cb = ComboboxFrame(self, ["'Normal'","Binomial","Geometric"],self.set_distribution)
# #         self.settings=tk.Frame(self,bg="lightgray")
# #         self.eandvar=tk.Frame(self,bg="dimgrey")
# #         self.dice=tk.Frame(self,bg="darkgrey")
# #
# #         #self.success_vals=[6]
# #         self.show_real=False
# #
# #         self.grid_config()
# #         self.place_widgets()
# #
# #     def grid_config(self):
# #         self.grid_columnconfigure(0, weight=4)
# #         self.grid_columnconfigure(1, weight=1)
# #
# #         self.grid_rowconfigure(0, weight=1)
# #         self.grid_rowconfigure(1, weight=2)
# #         self.grid_rowconfigure(2, weight=6)
# #         self.grid_rowconfigure(3, weight=1)
# #
# #     def place_widgets(self):
# #         self.graph.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(10,5), pady=10)
# #         self.cb.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
# #         self.settings.grid(row=1, column=1, sticky="nsew", padx=(5,10),pady=5)
# #         self.eandvar.grid(row=3,column=1, sticky="nsew", padx=(5,10),pady=5)
# #         self.dice.grid(row=2, column=1, sticky="nsew", padx=(5,10),pady=(5,10))
# #
# #
# #     def set_distribution(self,dist_type):
# #         match dist_type:
# #             case "Geometric":
# #                 params={"num":Parameter("num trials",1,99999,1,1),}
# #                 self.cb.setdefinition(r"$X \sim \text{Geo}(p)$")
# #                 self.model=GeoDice(params)
# #                 self.settings = DicetributionSettingsFrame(self, params, self.refresh)
# #
# #             case "'Normal'":
# #                 params={"n":Parameter("n",25,999,1,25),
# #                         "num":Parameter("num trials",1,99999,1,1),}
# #                 self.cb.setdefinition(r"$\overline{X} \sim N\left(\mu, \frac{\sigma^2}{n}\right)$")
# #                 self.model=NormDice(params,self.refresh)
# #                 self.settings = DicetributionSettingsFrame(self, params, self.refresh,success_vals_required=False)
# #
# #             case "Binomial":
# #                 self.cb.setdefinition(r"$X \sim B(n, p)$")
# #                 params={"n":Parameter("n",1,999,1,10),
# #                         "num":Parameter("num trials",1,99999,1,1),}
# #                 self.model= BinDice(params, self.refresh)
# #                 self.settings = DicetributionSettingsFrame(self, params, self.refresh)
# #
# #         self.graph = DicetributionGraph(self)
# #         self.refresh()
# #
# #     def refresh(self,success_vals=None,show_real=None):
# #         if success_vals is not None:
# #             self.model.success_vals = success_vals
# #
# #         if show_real is not None:
# #             self.show_real = show_real
# #
# #         self.eandvar=TwoLabels(self,["E(X)","Var(X)"]+["real E(X)","real Var(X)"]*self.show_real,self.model.EandVar(self.show_real))
# #
# #         self.model.add_dice_row(n=self.model.parameters["num"].value-self.model.get_n_dice_row())
# #         data=self.model.get_plot_data(self.show_real)
# #         self.graph.update_plot(*data)
# #         self.dice=DiceCanvas(self,self.model.get_dice_data())
# #         self.place_widgets()
#
# class DisController:
#     def __init__(self,view):
#         self.view=view
#         self.menubar = None
#
#         self.model=None
#         self.piecewise_type="Cubic Splines"
#         self.shadedict={"shadeinclmin":None,"shadeinclmax":None}
#         self.show_real=False
#
#     def set_distribution(self,dist_type):
#         latex=""
#         settings_args=[]
#         settings_kwargs={}
#         match dist_type:
#             case "Normal":
#                 latex=r"$X \sim N(\mu, \sigma^2)$"
#                 params = {"mu": Parameter("μ", -999, 999, 0.1, 0),
#                           "sigma": Parameter("σ", 0.1, 999, 0.1, 1)}
#                 self.model=Normal(params)
#                 settings_args=[params,self.refresh]
#             case "Binomial":
#                 latex=r"$X \sim B(n, p)$"
#                 params={"n":Parameter("n",1,999,1,10),
#                         "p":Parameter("p",0,1,0.01,0.5)}
#                 self.model=Binomial(params)
#                 settings_args = [params, self.refresh]
#             case "Exponential":
#                 latex=r"$X \sim \text{Exp}(\lambda)$"
#                 params={"lambda":Parameter("λ",0,999,.1,5)}
#                 self.model=Exponential(params)
#                 settings_args=[params,self.refresh]
#             case "Poisson":
#                 latex=r"$X \sim \text{Poi}(\lambda)$"
#                 params = {"lambda": Parameter("λ", 0, 999, .1, 5)}
#                 self.model = Poisson(params)
#                 settings_args = [ params, self.refresh]
#             case "Geometric":
#                 latex=r"$X \sim \text{Geo}(p)$"
#                 params = {"p": Parameter("p", 0, 1, 0.01, 0.5)}
#                 self.model = Geometric(params)
#                 settings_args = [ params, self.refresh]
#         self.view.set_definition(latex)
#         self.view.set_settings("Dis",*settings_args,**settings_kwargs)
#         self.view.set_graph("Dis")
#         self.view.update_dice_or_calc("calc",self.model,self.shadebetween)
#         self.refresh()
#
#     def shadebetween(self,shadedict):
#         self.shadedict=shadedict
#         self.refresh()
#
#     def refresh(self):
#         labels = ["E(X)", "Var(X)"]
#         values = [self.model.expectation(), self.model.variance()]
#         self.view.update_e_and_var(labels, values)
#
#         x_vals, y_vals, graph_type, cdf_func = self.model.get_plot_data()
#         graph_args=[x_vals,y_vals,graph_type]
#         kwargs={"cdf_func":cdf_func, **self.shadedict}
#         self.view.update_graph(*graph_args,**kwargs)
#
#     def initialise_view(self,view,root):
#         self.view = view
#         self.view.set_options(["Normal", "Binomial", "Exponential", "Poisson", "Geometric"])
#
# class PieceController:
#     def __init__(self,view):
#
#         self.view=view
#         self.model=None
#
#         self.piecewise_type="Cubic Splines"
#
#         self.shadedict={"shadeinclmin":None,"shadeinclmax":None}
#
#     def initialise_view(self,view,root):
#         self.view = view
#         self.view.set_options(["Piecewise"])
#
#     def set_distribution(self,dist_type):
#         settings_args = []
#         settings_kwargs = {}
#         graph_args = []
#         latex=""
#
#         match dist_type:
#             case "Piecewise":
#                 self.model = Piecewise([(1, 1), (2, 3), (3, 2)])
#                 settings_args=[self.set_piecewise_type,self.handle_add_point,self.handle_remove_point,self.handle_normalise]
#                 graph_args=[self,self.handle_add_point]
#         self.view.set_definition(latex)
#         self.view.set_settings("Piece",*settings_args,**settings_kwargs)
#         self.view.set_graph("Piece",*graph_args)
#         self.view.update_dice_or_calc("calc",self.model,self.shadebetween)
#
#         self.refresh()
#
#     def set_piecewise_type(self, piecewise_type="Cubic Splines"):
#         self.piecewise_type = piecewise_type
#         self.refresh()
#         self.view.refresh_calc()
#
#     def point_moved(self, old_x, old_y, new_x, new_y):
#         self.model.update_point(old_x, old_y, new_x, new_y)
#         self.refresh()
#         self.view.refresh_calc()
#
#     def handle_add_point(self, point=None):
#         self.model.add_point(point=point)
#         self.refresh()
#         self.view.refresh_calc()
#
#     def handle_remove_point(self):
#         self.model.remove_point()
#         self.refresh()
#         self.view.refresh_calc()
#
#     def handle_normalise(self):
#         self.model.normalise()
#         self.refresh()
#         self.view.refresh_calc()
#
#     def shadebetween(self,shadedict):
#         self.shadedict=shadedict
#         self.refresh()
#
#     def refresh(self):
#         labels = ["E(X)", "Var(X)"]
#         values = [self.model.expectation(), self.model.variance()]
#         self.view.update_e_and_var(labels, values)
#
#
#         points = self.model.get_points()
#         self.model.calculate_pieces(linear=(self.piecewise_type == "Linear"))
#         self.view.update_graph(points, self.model.pieces, **self.shadedict, cdf_func=self.model.cdf)
#
# class DiceController:
#     def __init__(self,view):
#         self.view=view
#         self.model=None
#
#         self.show_real=False
#
#     def set_distribution(self,dist_type):
#         settings_args = []
#         settings_kwargs = {}
#         latex=""
#         match dist_type:
#             case "Geometric":
#                 params = {"num": Parameter("num trials", 1, 99999, 1, 1), }
#                 latex=r"$X \sim \text{Geo}(p)$"
#                 self.model = GeoDice(params)
#                 settings_args = [params, self.refresh]
#
#             case "'Normal'":
#                 params = {"n": Parameter("n", 25, 999, 1, 25),
#                           "num": Parameter("num trials", 1, 99999, 1, 1), }
#                 latex=r"$\overline{X} \sim N\left(\mu, \frac{\sigma^2}{n}\right)$"
#                 self.model = NormDice(params, self.refresh)
#                 settings_args = [params, self.refresh]
#                 settings_kwargs={"success_vals_required":False}
#
#             case "Binomial":
#                 latex=r"$X \sim B(n, p)$"
#                 params = {"n": Parameter("n", 1, 999, 1, 10),
#                           "num": Parameter("num trials", 1, 99999, 1, 1), }
#                 self.model = BinDice(params, self.refresh)
#                 settings_args = [params, self.refresh]
#
#         self.view.set_definition(latex)
#         self.view.set_settings("Dice",*settings_args,**settings_kwargs)
#         self.view.set_graph("Dice")
#         self.refresh()
#
#     def refresh(self,success_vals=None,show_real=None):
#         if success_vals is not None:
#             self.model.success_vals = success_vals
#
#
#         if show_real is not None:
#             self.show_real = show_real
#
#
#         labels=["E(X)","Var(X)"]+["real E(X)","real Var(X)"]*self.show_real
#         values=self.model.e_and_var(self.show_real)
#         self.view.update_e_and_var(labels, values)
#
#         self.model.add_dice_row(n=self.model.parameters["num"].value-self.model.get_n_dice_row())
#         data=self.model.get_plot_data(self.show_real)
#         self.view.update_graph(*data)
#
#         self.view.update_dice_or_calc("dice",self.model.get_dice_data())
#
#     def initialise_view(self,view,root):
#         self.view=view
#         self.view.set_options(["'Normal'", "Binomial", "Geometric"])
#
#
# if __name__ == '__main__':
#
#     root = tk.Tk()
#     root.geometry("900x600")
#
#     controller = MEGAController(None)
#     view = View(root, controller)
#     controller.view = view
#
#     view.pack(fill="both", expand=True)
#     root.mainloop()