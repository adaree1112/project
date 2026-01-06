import tkinter as tk
from tkinter import ttk

class TestFrame (tk.Frame):
     def __init__(self, master=None):
          super().__init__(master)
          self.l1=tk.Label(self,text="P(X",width=2)
          self.cb=ttk.Combobox(self,values=["<","≤","=","≥",">"],width=2)
          self.e1=tk.Entry(self,width=4)
          self.l2=tk.Label(self,text=")=",width=2)
          self.e2=tk.Entry(self,width=4)

          self.place_widgets()

     def place_widgets(self):
         self.l1.pack(side=tk.LEFT)
         self.cb.pack(side=tk.LEFT)
         self.e1.pack(side=tk.LEFT)
         self.l2.pack(side=tk.LEFT)
         self.e2.pack(side=tk.LEFT)

class CalcFrame(tk.Frame):
    def __init__(self, master, distribution="Normal"):#
        super().__init__(master)
        self.dist=distribution

        self.l1 = tk.Label(self, text="P(X", width=2)
        self.cb = ttk.Combobox(self, values=["<", "≤"]+["="]*(self.dist!="Normal")+["≥", ">","< <", "≤ ≤"], width=2)
        self.e1 = tk.Entry(self, width=4)
        self.l2 = tk.Label(self, text=")=", width=2)
        self.e2 = tk.Entry(self, width=4)

        self.l1a = tk.Label(self, text="P(", width=2)
        self.l1bvar=tk.StringVar(self)
        self.l1bvar.set("X")


        self.l1b = tk.Label(self, textvariable=self.l1bvar, width=2)
        self.e3 = tk.Entry(self, width=4)

        self.e1.bind('<KeyRelease>', self.e1_updating)
        self.e2.bind('<KeyRelease>', self.e2_updating)
        # self.e3.bind('<KeyRelease>', self.e3_updating)

        self.cb.bind("<<ComboboxSelected>>",self.refresh)

        self.place_widgets()

    def place_widgets(self):
        for widget in self.winfo_children():
            widget.pack_forget()
        if self.cb.get() != "< <" and self.cb.get() != "≤ ≤":
            self.l1.pack(side="left")
            self.cb.pack(side="left")
        else:
            self.l1a.pack(side="left")
            self.e3.pack(side="left")
            self.l1b.pack(side="left")
            self.cb.pack(side="left")




        self.e1.pack(side="left")
        self.l2.pack(side="left")
        self.e2.pack(side="left")

    def refresh(self, *args):
        self.l1bvar.set(str(self.cb.get())[0]+"X")
        self.place_widgets()

    def e1_updating(self, *args):
        inp = self.e1.get()
        if not (inp.isalnum() or inp in ["", " ", "-"","]):
            try:
                x=float(inp)
            except ValueError:
                x= 0

        if self.cb.get() in "<≤=≥>":
            self.e2.delete(0, tk.END)
            self.e2.insert(0, str(3))
        else:
            self.e2.delete(0, tk.END)

    def e2_updating(self, *args):
        inp = self.e2.get()
        if not (inp.isalnum() or inp in ["", " ", "-"","]):
            try:
                x = float(inp)
            except ValueError:
                x = 0
######################################################
        self.e1.delete(0, tk.END)
        self.e1.insert(0, str(3))


if __name__ == "__main__":
     root=tk.Tk()
     w=150
     h=60
     root.geometry(f"{w}x{h}+100+100")
     root.resizable(1,1)
     root.title("Test Frame")
     main_frame=CalcFrame(root)
     main_frame.pack(fill=tk.BOTH, expand=True  )
     root.mainloop()