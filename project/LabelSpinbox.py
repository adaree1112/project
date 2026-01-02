import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk

from Piecewise import Parameter


class LabelSpinbox(tk.Frame):
    """
    Custom tkinter widget that contains a label and a spinbox with validation
    This allows user interaction with a Parameter

    Attributes
    ----------
    parameter : Parameter
        The Parameter instance that defines the spinbox behavior.
    on_change : Callable
        The callback function to be called when the value changes.
    value : tk.StringVar
        Tkinter variable holding the current value of the spinbox.
    text : tk.StringVar
        Tkinter variable holding the label text.
    label : tk.Label
        The label widget displaying the text.
    spin_box : ttk.Spinbox
        The spinbox widget for numeric or string input.
    """
    def __init__(self, master: tk.Widget, parameter: Parameter, on_change: callable) -> None:
        """
        Initialises the LabelSpinbox widget.

        Parameters
        ----------
        master : tk.Widget
            The parent widget to attach the widget to.
        parameter : Parameter
            The Parameter that the LabelSpinbox is being used to control.
        on_change : callable
            A callback for when the value is changed, so that the rest of the view can update.
        """
        super().__init__(master)
        self.parameter = parameter
        self.on_change = on_change

        self.value = tk.StringVar(self, self.parameter.value)
        self.text = tk.StringVar(self, self.parameter.get_label())

        v_cmd = (self.register(self.validate), '%P')

        self.label = tk.Label(self, textvariable=self.text)
        self.spin_box = ttk.Spinbox(self, textvariable=self.value, **self.parameter.get_spinbox_args(),
                                    validatecommand=v_cmd, validate="key", )

        self.value.trace_add("write", self._on_value_change)
        self.place_widgets()

    def validate(self, new_value: str) -> bool:
        """
        Validates the new value entered into the spinbox.

        Parameters
        ----------
        new_value:str
            The value that the user has entered

        Returns
        -------
        bool
            True if validation is successful, False otherwise.
        """
        return self.parameter.validate(new_value)

    def place_widgets(self) -> None:
        """
        Places the label and spinbox widgets in the frame using a grid layout.
        """
        self.label.grid(row=0, column=0, sticky="nsew")
        self.spin_box.grid(row=0, column=1, sticky="nsew")

    def _on_value_change(self, *_args) -> None:
        """
        Updates the value stored in the parameter and calls the on_change callback.

        This method is called when the spinbox is modified.

        Parameters
        ----------
        *args
            Arguments passed by the trace_add callback when the value changes.
        """
        self.parameter.value = self.value.get()
        self.on_change()


class PairRadioButton(tk.Frame):
    """
    Custom tkinter widget that allows the user to select one option from a set of radio buttons.

    Attributes
    ----------
    options : list of strings
        The list of options that the user can select from.
    v : tk.StringVar
        Tkinter variable holding the value of the selected radio button.
    on_change : Callable
        The callback function to be called when the value changes.
        """
    def __init__(self, master:tk.Widget, options:list[str], on_change:callable) -> None:
        """
        Initialises the PairRadioButton widget with the given options.

        Parameters
        ----------
        master: tk.Widget
            The parent widget to attach the frame to
        options : list of strings
            The list of options that the user can select from.
        on_change : callable
            The callback function to be called when the value changes.
        """
        super().__init__(master)
        #self.grid_propagate(False)

        self.on_change = on_change
        self.options = options
        self.v = tk.StringVar(master, "0")
        values = {option: i for i, option in enumerate(options)}

        for i, (text, value) in enumerate(values.items()):
            ttk.Radiobutton(self, text=text, variable=self.v, value=value, command=self.on_option_change).grid(column=i,
                                                                                                               row=0)

    def on_option_change(self)->None:
        """
        Callback function that is called when the user selects a different radio button.

        This method updates the selected type in the on_change callback.
        """
        self.on_change(piecewise_type=self.options[int(self.v.get())])

    def get(self)->str:
        """
        Returns the currently selected option from the radio buttons.

        Returns
        -------
        str
            The option text of the selected radio buttons.
        """
        return self.options[int(self.v.get())]


class DiceChoices(tk.Frame):
    """
    A Custom Tkinter widget that allows the user to select dice by clicking on dice images.

    The user may select as many as they want.

    Attributes
    ----------
    states : list of bool
        A list of boolean values representing the selection state of each die.
        True for selected
        False otherwise.
    labels : list of tk.Label
        A list that stores all the Labels
    """
    def __init__(self, master : tk.Widget, on_change:callable) -> None:
        """
        Initializes the DiceChoices widget.

        Creates 6 dice, grids them, binds them to the toggle function with the correct index, and appends them to the list
        Dice 6's state is set to True

        Parameters
        ----------
        master : tk.Widget
            The parent widget to attach the frame to
        on_change : callable
            A callback function to be called when the selection changes.
        """
        super().__init__(master)
        self.on_change = on_change
        self.states = [False] * 6
        self.labels = []

        for i in range(1, 7):
            label = tk.Label(self, image=get_dice_image(i),
                             relief='raised', borderwidth=2,
                             cursor='hand2')
            label.grid(column=i - 1, row=0)

            label.bind('<Button-1>', lambda e, idx=i - 1: self.toggle(idx))
            self.labels.append(label)

        self.toggle(5, callback=False)

    def toggle(self, index:int, callback:bool=True)->None:
        """
        Toggles the selection state of a die at the specified index.

        Parameters
        ----------
        index : int
            The index of the dice to toggle (0-5, corresponding to dice 1-6)
        callback : bool
            Whether to call the 'on_option_change' callback function after toggling the state.
            This is only false when the 6th die's is initially set to True.
        """

        self.states[index] = not self.states[index]

        if sum(self.states) != 0:

            if self.states[index]:
                self.labels[index].config(relief='sunken', bg='lightgray')
            else:
                self.labels[index].config(relief='raised', bg='SystemButtonFace')

            # Call the on_change callback
            if callback:
                self.on_option_change()
        else:
            self.states[index] = not self.states[index]

    def on_option_change(self)->None:
        """
        Calls the `on_change` callback with the list of selected dice values.

        This method is triggered when the selection state of any dice is changed.
        This method is not triggered when the 6th die's state is initially set to True.
        """
        selected = self.get_selected()
        self.on_change(success_vals=selected)

    def get_selected(self)->list[int]:
        """
        Generates a list of the values of the selected dice.

        Returns
        -------
        list[int]
            A list of integers representing the selected dice (1-6).
        """
        return [i + 1 for i, state in enumerate(self.states) if state]


class TwoLabels(tk.Frame):
    """
    A custom tkinter widget that displays two columns of labels: one for names and one for values.
    """
    def __init__(self, master:tk.Widget, names:list[str], values:list[float])-> None:
        """
        Initialises the TwoLabels widget with the given names and values.

        Parameters
        ----------
        master : tk.Widget
            the parent widget to attach the frame to
        names : list of strings
            The names that will be displayed on the first column
        values : list of floats
            The values that will be displayed on the second column, to 2 d.p.
        """
        super().__init__(master)

        for i, (name, value) in enumerate(zip(names, values)):
            tk.Label(self, text=name).grid(column=0, row=i)
            tk.Label(self, text=f"{value:.2f}").grid(column=1, row=i)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        for i in range(len(names)):
            self.grid_rowconfigure(i, weight=1)


dice_dict = {}
size = (30, 30)

def get_dice_image(number:int)->tk.PhotoImage:
    """
    Returns dice image for the specified number.

    If the image has already been generated, it will be returned from the dice_dict cache.
    If not, it loads, resizes and caches the image

    Parameters
    ----------
    number : int
        The number of the dice (1-6) for which the image is requested.

    Returns
    -------
    tk.PhotoImage
        The PhotoImage object representing the resized dice image.
    """
    if number not in dice_dict:
        image = Image.open(f'project/assets/dice/dice-{number}.png').resize(size, Image.Resampling.LANCZOS)
        dice_dict[number] = ImageTk.PhotoImage(image)
    return dice_dict[number]


