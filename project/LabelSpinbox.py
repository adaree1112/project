import tkinter as tk
import tkinter.ttk as ttk

from Piecewise import Parameter

class LabelSpinbox(tk.Frame):
    def __init__(self, master,parameter: Parameter,on_change):
        super().__init__(master)
        self.parameter = parameter
        self.on_change = on_change

        self.value = tk.StringVar(self,self.parameter.value)
        self.text = tk.StringVar(self,self.parameter.get_label())

        vcmd = (self.register(self.validate), '%P')


        self.label = tk.Label(self, textvariable=self.text)
        self.sb = ttk.Spinbox(self,textvariable=self.value,**self.parameter.get_spinbox_args(),validatecommand=vcmd,validate="key",)

        self.value.trace_add("write", self._on_value_change)
        self.place_widgets()

    def validate(self, new_value):
        return self.parameter.validate(new_value)

    def place_widgets(self):
        self.label.grid(row=0, column=0, sticky="nsew")
        self.sb.grid(row=0, column=1, sticky="nsew")

    def _on_value_change(self, *args):
        self.parameter.value = self.value.get()
        self.on_change()

class PairRadioButton(tk.Frame):
    def __init__(self, master, options,on_change):
        super().__init__(master)
        self.on_change = on_change
        self.options = options
        self.v = tk.StringVar(master, "0")
        values = {option:i for i, option in enumerate(options)}

        for i,(text, value) in enumerate(values.items()):
            ttk.Radiobutton(master, text=text, variable=self.v,value=value,command=self.on_option_change).grid(column=i,row=0)

    def on_option_change(self):
        self.on_change(piecewise_type=self.options[int(self.v.get())])

    def get(self):
        return self.options[int(self.v.get())]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("TEST")

    def callback(a=None,*args):
        print("hello2",a)
        pass


    controller = PairRadioButton(root,["Linear","Cubic Splines"],callback)
    #controller = LabelSpinbox(root,Parameter("p",0,1,0.01,0.5),callback)
    controller.grid(row=0,column=0)
    root.mainloop()