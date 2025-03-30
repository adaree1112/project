import tkinter as tk
from tkinter import ttk
from Simulation import Simulation

class Home(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.menu=ttk.Combobox(self, values=["Game","Simulation","Ideal"])
        self.welcome=tk.Label(self, text="Welcome, please select an option and click start")
        self.start = tk.Button(self, text="Start",command=self.openwindow)

        self.place_widgets()

    def place_widgets(self):
        self.welcome.pack()
        self.menu.pack()
        self.start.pack()

    def openwindow(self):
        if self.menu.get() == "Game":
            pass
        elif self.menu.get() == "Simulation":
            w = 400
            h = 300
            newWindow = tk.Toplevel(self.master)
            newWindow.title("Simulation")
            newWindow.geometry(f"{w}x{h}+100+100")
            newWindow.resizable(True, True)
            frame = Simulation(newWindow)
            frame.pack(fill=tk.BOTH, expand=True)

        elif self.menu.get() == "Ideal":
            pass




if __name__ == "__main__":
    root = tk.Tk()
    w = 300
    h = 100
    root.geometry(f"{w}x{h}+100+100")
    root.resizable(True, True)
    root.title("Home")
    main_frame = Home(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
