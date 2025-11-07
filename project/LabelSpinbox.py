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
        if self.on_change:
            self.on_change(self.parameter.value)

if __name__ == "__main__":
    #################################SOME ERRORS
    root = tk.Tk()
    root.title("TEST")

    def callback(*args):
        print("hello2")
        pass

    # 2. Create the Controller, which creates and manages the View
    controller = LabelSpinbox(root,Parameter("p",0,1,0.01,0.5),callback)
    controller.pack()
    root.mainloop()