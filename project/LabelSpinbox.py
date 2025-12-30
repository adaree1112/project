import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk

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

class DiceChoices(tk.Frame):
    def __init__(self, master, on_change):
        super().__init__(master)
        self.on_change = on_change
        self.states = [False] * 6
        self.vars = []
        self.labels = []

        for i in range(1,7):
            label = tk.Label(self, image=get_dice_image(i),
                             relief='raised', borderwidth=2,
                             cursor='hand2')
            label.grid(column=i - 1, row=0)

            label.bind('<Button-1>', lambda e, idx=i - 1: self.toggle(idx))
            self.labels.append(label)

        self.toggle(5,callback=False)

    def toggle(self, index,callback=True):

        self.states[index] = not self.states[index]

        if sum(self.states)!=0:

            if self.states[index]:
                self.labels[index].config(relief='sunken', bg='lightgray')
            else:
                self.labels[index].config(relief='raised', bg='SystemButtonFace')

            # Call the on_change callback
            if callback:
                self.on_option_change()
        else:
            self.states[index] = not self.states[index]

    def on_option_change(self):
        selected = self.get_selected()
        self.on_change(success_vals=selected)

    def get_selected(self):
        return [i+1 for i,state in enumerate(self.states) if state]


class TwoLabels(tk.Frame):
    def __init__(self, master, names,values):
        super().__init__(master)
        self.names = names
        self.values = values

        for i,(name,value) in enumerate(zip(names,values)):
            tk.Label(self, text=name).grid(column=0, row=i)
            tk.Label(self, text=f"{value:.2f}").grid(column=1, row=i)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        for i in range(len(names)):
            self.grid_rowconfigure(i, weight=1)

dice_dict = {}
size = (30, 30)
def get_dice_image(number):
    if number not in dice_dict:
        image = Image.open(f'assets/dice/dice-{number}.png').resize(size, Image.Resampling.LANCZOS)
        dice_dict[number] = ImageTk.PhotoImage(image)
    return dice_dict[number]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("TEST")

    def callback(*args,**kwargs):
        print(args)
        pass

    controller=DiceChoices(root,callback)
    #controller=TwoLabels(root,["A","B"],[1,2])
#    controller = PairRadioButton(root,["Linear","Cubic Splines"],callback)
    #controller = LabelSpinbox(root,Parameter("p",0,1,0.01,0.5),callback)
    controller.grid(row=0,column=0)
    root.mainloop()