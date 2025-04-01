import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Distributions import sim_Bin, ideal_Bin, sim_Geo, ideal_Geo, sim_Normal,ideal_Normal
import numpy as np



class GeometricOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        super().__init__(master)
        self.onrelease = onrelease
        self.p = tk.Label(self, text="p", )
        self.pentry = tk.Entry(self)
        self.pentry.bind("<KeyRelease>", self.onKeyRelease)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()


class BinomialOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        super().__init__(master)
        self.onrelease = onrelease
        self.p = tk.Label(self, text="p", )
        self.pentry = tk.Entry(self)
        self.n = tk.Label(self, text="n", )
        self.nentry = tk.Entry(self)
        self.nentry.bind("<KeyRelease>", self.onKeyRelease)
        self.pentry.bind("<KeyRelease>", self.onKeyRelease)

        self.place_widgets()

    def place_widgets(self):
        self.p.grid(column=0, row=0, sticky="nsew")
        self.pentry.grid(column=1, row=0, sticky="nsew")
        self.n.grid(column=0, row=1, sticky="nsew")
        self.nentry.grid(column=1, row=1, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()


class NormalOFrame(tk.Frame):
    def __init__(self, master, onrelease):
        self.onrelease = onrelease

        super().__init__(master)
        self.mu = tk.Label(self, text="μ", )
        self.muentry = tk.Entry(self)
        self.sig = tk.Label(self, text="σ", )
        self.sigentry = tk.Entry(self)
        self.muentry.bind("<KeyRelease>", self.onKeyRelease)
        self.sigentry.bind("<KeyRelease>", self.onKeyRelease)
        self.place_widgets()

    def place_widgets(self):
        self.mu.grid(column=0, row=0, sticky="nsew")
        self.muentry.grid(column=1, row=0, sticky="nsew")
        self.sig.grid(column=0, row=1, sticky="nsew")
        self.sigentry.grid(column=1, row=1, sticky="nsew")

    def onKeyRelease(self, event):
        self.onrelease()


class GeometricGFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Reference to the Application class
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = None  # Initialize canvas to None

        self.plot_graph()  # Initial plot

    def plot_graph(self):
        # Clear the existing plot
        self.ax.clear()
        try:
            p_str = self.master.current_O_frame.pentry.get()
            num_str = self.master.num.get()
            if not p_str:
                raise ValueError("Please enter values for p.")
            if int(num_str) < 1:
                raise ValueError("Please enter values for num")
            p = float(p_str)
            num = int(num_str)

            if not (0 <= p <= 1):
                raise ValueError("p must be between 0 and 1.")

            # Generate data for Binomial Distribution
            results = [sim_Geo(p) for _ in range(num)]  # List of results from sim_Bin
            # Count the occurrences of each result
            counts = {}
            for result in results:
                counts[result] = counts.get(result, 0) + 1

            if not self.master.ideal.get():
                # Prepare data for plotting
                x = range(max(results) + 1)  # Possible number of successes
                y = [counts.get(i, 0) / num for i in x]  ####################################################################################ERRORS OCCUR HERE

                # Plot the bar chart
                self.ax.bar(x, y, color="lightgreen")

                self.ax.set_title(f"Geometric Distribution (Simulated {num} trials)")
                self.ax.set_xlabel("Number of Trials Required for a Success")
                self.ax.set_ylabel("Probability")

            else:
                x1 = list(counts.keys())  # Possible number of successes
                x2 = range(max(results) + 1)
                y1 = [counts.get(i, 0) / num for i in x2]####################################################################################ERRORS OCCUR HERE
                y2 = [ideal_Geo(r, p) for r in x2]

                bar_width = 0.35
                index = range(len(x2))
                self.ax.bar(index, y1, bar_width, color="lightgreen", label="Simulation 1")
                # Plot the second set of bars, shifted to the right
                self.ax.bar([i + bar_width for i in index], y2, bar_width, color="orange", label="Ideal")

                self.ax.set_title(f"Geometric Distribution (Simulated {num} trials)")
                self.ax.set_xlabel("Number of Trials Required for a Success")
                self.ax.set_ylabel("Probability")
                self.ax.set_xticks([i + bar_width / 2 for i in index])  # Set x-ticks in the middle of the two bars
                self.ax.set_xticklabels(x2)  # Label the x-ticks with the number of successes
                self.ax.legend()

        except ValueError as e:
            # Handle cases when n or p are not entered or invalid
            self.ax.text(0.5, 0.5, str(e),
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=12, color='red')  # Show error message

        # Update the canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  # Destroy the old canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


class BinomialGFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Reference to the Application class
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = None  # Initialize canvas to None

        self.plot_graph()  # Initial plot

    def plot_graph(self):
        # Clear the existing plot
        self.ax.clear()
        try:
            n_str = self.master.current_O_frame.nentry.get()
            p_str = self.master.current_O_frame.pentry.get()
            num_str = self.master.num.get()
            if not n_str or not p_str:
                raise ValueError("Please enter values for n and p.")
            if int(num_str) < 1:
                raise ValueError("Please enter values for num")
            n = int(n_str)
            p = float(p_str)
            num = int(num_str)

            if not (0 <= p <= 1):
                raise ValueError("p must be between 0 and 1.")

            if n < 0:
                raise ValueError("n must be a non-negative integer.")

            # Generate data for Binomial Distribution
            results = [sim_Bin(n, p) for _ in range(num)]  # List of results from sim_Bin
            # Count the occurrences of each result
            counts = {}
            for result in results:
                counts[result] = counts.get(result, 0) + 1
            if not self.master.ideal.get():
                # Prepare data for plotting
                x = range(n + 1)  # Possible number of successes
                y = [counts.get(i, 0) / num for i in x]  # Number of times each success count occurred

                # Plot the bar chart
                self.ax.bar(x, y, color="lightgreen")

                self.ax.set_title(f"Binomial Distribution (Simulated {num} trials)")
                self.ax.set_xlabel("Number of Successes")
                self.ax.set_ylabel("Probability")

            else:
                x1 = list(counts.keys())  # Possible number of successes
                x2 = range(n + 1)
                y1 = [counts.get(i, 0) / num for i in x2]
                y2 = [ideal_Bin(n, r, p) for r in x2]

                bar_width = 0.35
                index = range(len(x2))
                self.ax.bar(index, y1, bar_width, color="lightgreen", label="Simulation 1")
                # Plot the second set of bars, shifted to the right
                self.ax.bar([i + bar_width for i in index], y2, bar_width, color="orange", label="Ideal")

                self.ax.set_title(f"Binomial Distribution (Simulated {num} trials, and ideal)")
                self.ax.set_xlabel("Number of Successes")
                self.ax.set_ylabel("Probability")
                self.ax.set_xticks([i + bar_width / 2 for i in index])  # Set x-ticks in the middle of the two bars
                self.ax.set_xticklabels(x2)  # Label the x-ticks with the number of successes
                self.ax.legend()





        except ValueError as e:
            # Handle cases when n or p are not entered or invalid
            self.ax.text(0.5, 0.5, str(e),
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=12, color='red')  # Show error message

        # Update the canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  # Destroy the old canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


class NormalGFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Reference to the Application class
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = None  # Initialize canvas to None

        self.plot_graph()  # Initial plot

    def plot_graph(self):
        # Clear the existing plot
        self.ax.clear()
        try:
            mu_str = self.master.current_O_frame.muentry.get()
            sig_str = self.master.current_O_frame.sigentry.get()
            num_str = self.master.num.get()
            if not mu_str or not sig_str:
                raise ValueError("Please enter values for μ and σ.")
            if int(num_str) < 1:
                raise ValueError("Please enter values for num")
            mu = float(mu_str)
            sig = float(sig_str)
            num = int(num_str)

            if sig == 0:
                raise ValueError("sig must not be equal to 0.")

            # Generate data for Binomial Distribution
            results = [sim_Normal(mu, sig) for _ in range(num)]  # List of results from sim_Bin
            # Count the occurrences of each result
            counts = {}
            for i in np.arange(int(min(results)) - 1, int(max(results)) + 1, 0.1):
                counts[i] = sum(1 for r in results if r < i) - sum(counts.values())
            if not self.master.ideal.get():
                # Prepare data for plotting
                x = np.arange(int(min(results)) - 1, int(max(results)) + 1, 0.1)  # Possible number of successes
                y = [counts.get(i, 0) / num  for i in x]  # Number of times each success count occurred

                # Plot the bar chart
                self.ax.bar(x, y, color="lightgreen")

                self.ax.set_title(f"Normal Distribution (Simulated {num} trials)")
                self.ax.set_xlabel("")
                self.ax.set_ylabel("Probability")

            else:
                x = np.arange(int(min(results)) - 1, int(max(results)) + 1, 0.1)  # Possible number of successes
                print(counts)
                y1 = [counts.get(i, 0) / num for i in x]  # Number of times each success count occurred
                print(y1)
                y2 = [ideal_Normal(mu, sig, xi) for xi in x]
                # Plot the bar chart
                self.ax.bar(x, y1, color="lightgreen", label="Simulation 1")
                self.ax.plot(x, y2, color="orange", label="Ideal")
                self.ax.set_title(f"Normal Distribution (Simulated {num} trials)")
                self.ax.set_xlabel("")
                self.ax.set_ylabel("Probability")

                self.ax.legend()





        except ValueError as e:
            # Handle cases when n or p are not entered or invalid
            self.ax.text(0.5, 0.5, str(e),
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=12, color='red')  # Show error message

        # Update the canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  # Destroy the old canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


class Simulation(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.combo = ttk.Combobox(self, width=5, values=["Geometric", "Binomial", "Normal"])
        self.dist = self.combo.get()
        self.current_O_frame = None
        self.current_G_frame = None
        self.combo.bind("<<ComboboxSelected>>", self.on_dist_change)
        self.ideal = tk.BooleanVar()
        self.idealtoggle = tk.Checkbutton(self, text="show ideal", offvalue=False, onvalue=True, variable=self.ideal,
                                          command=self.refreshG)
        self.num = tk.StringVar(value="0")
        self.numspinbox = ttk.Spinbox(self, width=5, textvariable=self.num, from_=0, to=100, command=self.on_num_change)

        self.place_widgets()

    def place_widgets(self):
        self.combo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        if self.current_O_frame and self.current_G_frame:
            self.current_O_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=10)
            self.current_G_frame.grid(row=0, rowspan=4, column=0, sticky=tk.NSEW, padx=10, pady=10)
            self.idealtoggle.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=10)
            self.numspinbox.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

    def on_dist_change(self, event):
        self.dist = self.combo.get()  # Update the distribution
        self.change_dist()

    def on_num_change(self):
        self.num.set(self.numspinbox.get())
        self.refreshG()

    def refreshG(self):
        if self.dist == "Geometric":
            self.current_G_frame = GeometricGFrame(self)
        elif self.dist == "Binomial":
            self.current_G_frame = BinomialGFrame(self)
        elif self.dist == "Normal":
            self.current_G_frame = NormalGFrame(self)

        self.place_widgets()

    def change_dist(self):
        # Destroy the current frame if it exists
        if self.current_O_frame:
            self.current_O_frame.destroy()
        if self.current_G_frame:
            self.current_G_frame.destroy()

        # Create a new frame based on the selected distribution
        if self.dist == "Geometric":
            self.current_O_frame = GeometricOFrame(self, self.refreshG)
            self.current_G_frame = GeometricGFrame(self)
        elif self.dist == "Binomial":
            self.current_O_frame = BinomialOFrame(self, self.refreshG)
            self.current_G_frame = BinomialGFrame(self)
        elif self.dist == "Normal":
            self.current_O_frame = NormalOFrame(self, self.refreshG)
            self.current_G_frame = NormalGFrame(self)

        self.place_widgets()
