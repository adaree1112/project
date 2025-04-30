import tkinter as tk
from tkinter import ttk

class TestFrame (tk.Frame):
     def __init__(self, master=None):
          super().__init__(master)
          self.l1=tk.Label(self,text="P(X",width=2)
          self.cb=ttk.Combobox(self,values=["<","≤","=","≥",">"],width=2)
          self.e1=tk.Entry(self,width=2)
          self.l2=tk.Label(self,text=")=",width=2)
          self.e2=tk.Entry(self,width=2)

          self.place_widgets()

     def place_widgets(self):
         self.l1.pack(side=tk.LEFT)
         self.cb.pack(side=tk.LEFT)
         self.e1.pack(side=tk.LEFT)
         self.l2.pack(side=tk.LEFT)
         self.e2.pack(side=tk.LEFT)

if __name__ == "__main__":
     root=tk.Tk()
     w=400
     h=300
     root.geometry(f"{w}x{h}+100+100")
     root.resizable(1,1)
     root.title("Test Frame")
     main_frame=TestFrame(root)
     main_frame.pack(fill=tk.BOTH, expand=True)
     root.mainloop()