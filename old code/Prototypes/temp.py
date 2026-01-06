from tkinter import *
import tkinter as tk


class TempConverter:
    def __init__(self, kelvin):
        # the _ shows that it's private
        self._kelvin = kelvin

    # kelvin() is a getter function
    @property
    def kelvin(self):
        return self._kelvin

    @kelvin.setter
    def kelvin(self, new_kelvin):
        self._kelvin = new_kelvin

    @property
    def celsius(self):
        return self._kelvin - 273.15

    @celsius.setter
    def celsius(self, celsius):
        self._kelvin = celsius + 273.15

    @property
    def fahrenheit(self):
        return 1.8 * (self._kelvin - 273) + 32

    @fahrenheit.setter
    def fahrenheit(self, fahrenheit):
        self._kelvin = (fahrenheit - 32) * 5 / 9 + 273.15


class GUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.temp = TempConverter(0)

        self.kelvin = tk.Label(self, text='Kelvin')
        self.celsius = tk.Label(self, text="Celsius")
        self.fahrenheit = tk.Label(self, text='Fahrenheit')
        self.clear = tk.Button(self, text='Clear', command=self.clear)

        self.kelvin_num = tk.Entry(self, text=f'{round(self.temp.kelvin, 2)}')
        self.celsius_num = tk.Entry(self, text=f'{round(self.temp.celsius, 2)}')
        self.fahrenheit_num = tk.Entry(self, text=f'{round(self.temp.fahrenheit, 2)}')

        # add events bind(<KeyRelease>, self.temp.fahrenheit)

        self.kelvin_num.bind('<KeyRelease>', self.k_updating)
        self.celsius_num.bind('<KeyRelease>', self.c_updating)
        self.fahrenheit_num.bind('<KeyRelease>', self.f_updating)

        self.kelvin_num.bind('<Double-Button-1>', self.clearing)
        self.celsius_num.bind('<Double-Button-1>', self.clearing)
        self.fahrenheit_num.bind('<Double-Button-1>', self.clearing)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=3)
        self.columnconfigure(0, weight=5)

        self.place_widgets()

    def place_widgets(self):
        placement_settings = {'padx': 5, 'pady': 5, 'sticky': 'we'}
        placement_settings1 = {'padx': 10, 'pady': 10, 'sticky': 'we'}

        self.kelvin.grid(row=0, column=0, **placement_settings)
        self.celsius.grid(row=1, column=0, **placement_settings)
        self.fahrenheit.grid(row=2, column=0, **placement_settings)
        self.clear.grid(row=1, column=1, **placement_settings)

        #         self.kelvin_num.grid(row=0, column=0, **placement_settings1)
        #         self.celsius_num.grid(row=1, column=0, **placement_settings1)
        #         self.fahrenheit_num.grid(row=2, column=0, **placement_settings1)

        self.kelvin_num.place(x=140, y=75)
        self.celsius_num.place(x=140, y=225)
        self.fahrenheit_num.place(x=140, y=350)

    def k_updating(self, a):
        inp = self.kelvin_num.get()
        if not (inp.isalpha() or inp in ["", " ", "-"","]):
            try:
                self.temp.kelvin = float(self.kelvin_num.get())
            except ValueError:
                self.temp.kelvin = 0

            self.celsius_num.delete(0, tk.END)
            self.celsius_num.insert(0, round(self.temp.celsius, 2))

            self.fahrenheit_num.delete(0, tk.END)
            self.fahrenheit_num.insert(0, round(self.temp.fahrenheit, 2))

    def c_updating(self, a):
        inp = self.celsius_num.get()
        if not (inp.isalpha() or inp in ["", " ", "-"","]):
            try:
                self.temp.celsius = float(self.celsius_num.get())
            except ValueError:
                self.temp.celsius = 0

            self.fahrenheit_num.delete(0, tk.END)
            self.fahrenheit_num.insert(0, round(self.temp.fahrenheit, 2))

            self.kelvin_num.delete(0, tk.END)
            self.kelvin_num.insert(0, round(self.temp.kelvin, 2))

    def f_updating(self, a):
        inp = self.fahrenheit_num.get()
        if not (inp.isalpha() or inp in ["", " ", "-"","]):
            try:
                self.temp.fahrenheit = float(self.fahrenheit_num.get())
            except ValueError:
                self.temp.fahrenheit = 0

            self.celsius_num.delete(0, tk.END)
            self.celsius_num.insert(0, round(self.temp.celsius, 2))

            self.kelvin_num.delete(0, tk.END)
            self.kelvin_num.insert(0, round(self.temp.kelvin, 2))

    def clearing(self, event):
        event.widget.delete(0, tk.END)

    def clear(self):
        self.kelvin_num.delete(0, tk.END)
        self.celsius_num.delete(0, tk.END)
        self.fahrenheit_num.delete(0, tk.END)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('400x400')
    root.title('Temperature converter app')

    main_frame = GUI(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()