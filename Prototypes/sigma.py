import tkinter as tk
import tkinter.ttk as ttk

class app(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.cb=ttk.Combobox(self, values=["σ","σ²"],width=2)
        self.l=tk.Label(self,text="=")
        self.sb=ttk.Spinbox(self, from_=1, to=100,width=5)

        self.place_widgets()

    def place_widgets(self):
        self.cb.pack(side="left")
        self.l.pack(side="left")
        self.sb.pack(side="left")

if __name__ == '__main__':
    root = tk.Tk()
    app = app(master=root)
    app.pack()
    root.mainloop()