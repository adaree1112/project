import tkinter as tk
import tkinter.ttk as ttk


class LabelSpinBox(tk.Frame):
    def __init__(self, root, label_text, mini, maxi, step, default, on_change):
        # Initialize the Frame
        super().__init__(root, padx=5, pady=5)
        self.text = tk.StringVar(value=label_text)
        self.label = tk.Label(self, textvariable=self.text)
        self.label.pack(side=tk.LEFT)
        self.default = default
        self.mini = mini
        self.maxi = maxi
        self.value = tk.StringVar(value=str(self.default))
        self.on_change = on_change

        self.spinbox = ttk.Spinbox(self,textvariable=self.value,from_=mini,to=maxi,increment=step,width=5,command=self.on_change)
        self.spinbox.bind("<Key>",self.validate_then_change)
        self.spinbox.pack(side=tk.LEFT)

    def get(self):
        try:
            return float(self.value.get())
        except ValueError:
            return 0.0

    def validate_then_change(self, event):
        try:
            if event.keysym in ["Up","Down"]:
                self.on_change()
            else:
                x=float(self.spinbox.get())
                if self.mini<x<self.maxi:
                    self.on_change()
                else:
                    raise ValueError
        except ValueError:
            self.spinbox.set(self.default)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Custom LabelSpinBox Demo')
    root.geometry('300x200')
    def hello():
        print('Hello World!')
    spinbox = LabelSpinBox(
        root,
        label_text="p = ",
        mini=0,
        maxi=1,
        step=0.01,
        default=0.5,
        on_change=hello
    )
    spinbox.pack(pady=10, padx=20)

    root.mainloop()