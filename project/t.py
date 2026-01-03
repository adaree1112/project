import tkinter as tk
from random import randint
import re

from project.Piecewise import Parameter
from project.LabelSpinbox import LabelSpinbox


class GameModel:
    def __init__(self,params):
        self.parameters = params

    @property
    def lower_bound(self):
        return int(self.parameters['l'].value)

    @property
    def upper_bound(self):
        return int(self.parameters['u'].value)

    @upper_bound.setter
    def upper_bound(self, value):
        self.parameters['u'].value = value

    @property
    def time_gap(self):
        return self.parameters['t'].value

    @property
    def number_of_numbers(self):
        return int(self.parameters['n'].value)

    def generate_number_sequence(self):
        lst=[]
        if self.number_of_numbers > 0:
            lst=[randint(self.lower_bound,self.upper_bound)]
        while len(lst)<self.number_of_numbers:
            if (x:=randint(self.lower_bound,self.upper_bound)) != lst[-1]:
                lst.append(x)
        return lst

class GameController:
    def __init__(self,view:'GameView'):
        self.view = view
        self.model = None

        self.game_running = False

        self.set_model()
        self.initialise_view()
        self.start_phase()

    def initialise_view(self):
        self.view.master.bind("<Escape>",self.stop_game)

    def stop_game(self,_event=None):
        self.game_running = False
        self.view.show_message("Game Stopped")
        self.start_phase()
        self.view.after(2000,lambda: self.view.show_message("")) # type: ignore


    def set_model(self):
        params = {"l": Parameter("lower", -100, 50, 5, -10),
                      "u": Parameter("upper", -50, 100, 5, 10),
                      "n": Parameter("number", 0, 100, 5, 10),
                      "t": Parameter("time gap", -100, 50, .5, 1), }
        self.model=GameModel(params)
        self.view.set_settings(params,self.validate_bounds)
        self.view.set_buttons({"Start":self.game_phase})
        self.view.set_entry(self.answer_phase)

    def validate_bounds(self):
        lower = self.model.lower_bound
        upper = self.model.upper_bound

        if lower >= upper:
            self.model.upper_bound = lower + self.model.parameters["u"].step

            for ls in self.view.settings.label_spinboxes:
                if ls.parameter == self.model.parameters["u"]:
                    ls.value.set(str(self.model.upper_bound))

    def start_phase(self):
        self.view.configure_for_start_phase()

    def game_phase(self):
        self.view.configure_for_game_phase()
        self.begin_game()

    def entry_phase(self,total):
        self.view.show_message("Input a guess:")
        self.view.configure_for_entry_phase(total)

    def begin_game(self):
        if self.game_running:
            return

        total = 0
        self.game_running = True
        nums=iter(self.model.generate_number_sequence())
        time_gap=self.model.time_gap
        if self.model.number_of_numbers>0:
            self.view.show_num(str(x:=next(nums)))
            total=x

        def show_num():
            nonlocal total
            if not self.game_running:
                return
            try:
                self.view.show_num(str(n:=next(nums)))
                total+=n
                self.view.after(int(time_gap * 1000), show_num) # type: ignore
            except StopIteration:
                self.game_running = False
                self.view.show_message("")
                self.entry_phase(total)

        self.view.after(int(time_gap * 1000), show_num) # type: ignore

    def answer_phase(self, guess,total):
        self.view.configure_for_answer_phase()
        if guess == total:
            self.view.show_message(f"Correct!\nThe answer was {total}")
        else:
            self.view.show_message(f"Wrong!\nYou guessed {guess}.\nCorrect answer was {total}.")
        self.start_phase()
        self.view.after(2000,lambda:self.view.show_message("")) # type: ignore

class EntryFrame(tk.Frame):
    def __init__(self,master,callback):
        super().__init__(master)
        self.grid_propagate(False)

        self.additional_parameter=None
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self,textvariable=self.entry_var,width=10)
        self.button = tk.Button(self,text="Submit",command=lambda:callback(int(self.entry_var.get()),self.additional_parameter) if re.match(r"^-?\d+$", self.entry_var.get()) else None,width=10)
        self.entry.bind("<Return>",lambda event:callback(int(self.entry_var.get()),self.additional_parameter) if re.match(r"^-?\d+$", self.entry_var.get()) else None)


        self.entry.grid(row=0,column=0,sticky="e")
        self.button.grid(row=0,column=1,sticky="w")

    def enable(self):
        self.button.config(state=tk.NORMAL)
        self.entry.config(state=tk.NORMAL)

    def disable(self):
        self.button.config(state=tk.DISABLED)
        self.entry.config(state=tk.DISABLED)
        self.entry_var.set("")

class ButtonsFrame(tk.Frame):
    def __init__(self,master,button_dict):
        super().__init__(master)
        self.grid_propagate(False)

        self.buttons=[]
        for i,(text,func) in enumerate(button_dict.items()):
            self.buttons.append(x:=tk.Button(self,text=text,command=func))
            x.grid(column=i,row=0)

    def enable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def disable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.DISABLED)

    def enable_button(self,text):
        for button in self.buttons:
            if button['text'] == text:
                button.config(state=tk.NORMAL)

    def disable_button(self,text):
        for button in self.buttons:
            if button['text'] == text:
                button.config(state=tk.DISABLED)

class GameSettingsFrame(tk.Frame):
    def __init__(self, master,parameters,on_change):
        super().__init__(master)
        self.grid_propagate(False)

        self.on_change = on_change
        self.label_spinboxes = []

        for param in parameters.values():
            self.label_spinboxes.append(x:=LabelSpinbox(self,param,self.on_change))
            x.pack()

    def enable_all_spinboxes(self):
        for label_spinbox in self.label_spinboxes:
            label_spinbox.spin_box.config(state=tk.NORMAL)

    def disable_all_spinboxes(self):
        for label_spinbox in self.label_spinboxes:
            label_spinbox.spin_box.config(state=tk.DISABLED)

class GameView(tk.Frame):
    def __init__(self,master):
        super().__init__(master)

        self.grid_propagate(False)

        self.num_screen=None
        self.buttons=None
        self.settings=None
        self.entry=None

        self.set_up_blank_view()

        self.place_widgets()
        self.grid_config()


    def set_up_blank_view(self):
        self.num_screen = tk.Label(self,bg="white",width=4)
        self.buttons = tk.Frame(self, bg="white")
        self.settings = tk.Frame(self,bg="lightgray")
        self.entry = tk.Frame(self,bg="darkgray")

    def grid_config(self):
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=2)

    def place_widgets(self):
        self.num_screen.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(10,5), pady=10)
        self.buttons.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.settings.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=(10,5))
        self.entry.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=(5, 10))

    def set_settings(self, *args,**kwargs):
        self.settings.destroy()
        self.settings = GameSettingsFrame(self, *args, **kwargs)
        self.settings.grid(row=0, column=1, sticky="nsew", padx=(5,10),pady=5)

    def set_buttons(self, *args,**kwargs):
        self.buttons.destroy()
        self.buttons = ButtonsFrame(self,*args,**kwargs)
        self.buttons.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=(10, 5))

    def set_entry(self,*args,**kwargs):
        self.entry.destroy()
        self.entry = EntryFrame(self,*args,**kwargs)
        self.entry.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=(5, 10))

    def configure_for_start_phase(self):
        self.settings.enable_all_spinboxes()
        self.buttons.enable_button("Start")
        self.entry.disable()
        self.place_widgets()

    def configure_for_game_phase(self):
        self.settings.disable_all_spinboxes()
        self.buttons.disable_button("Start")
        self.entry.disable()
        self.place_widgets()

    def configure_for_entry_phase(self, additional_parameter):
        self.settings.disable_all_spinboxes()
        self.buttons.disable_button("Start")
        self.entry.enable()
        self.entry.additional_parameter = additional_parameter
        self.place_widgets()

    def configure_for_answer_phase(self):
        self.settings.disable_all_spinboxes()
        self.buttons.disable_button("Start")
        self.entry.disable()
        self.place_widgets()

    def show_num(self,num):
        self.num_screen.config(text=str(num), font=("Courier",50))

    def show_message(self,text):
        self.num_screen.config(text=text,font=("Arial",15))



if __name__=="__main__":
    root = tk.Tk()
    the_view=GameView(root)
    controller=GameController(the_view)
    the_view.pack(expand=True, fill='both')
    root.resizable(False,False)
    root.geometry("600x400")

    root.mainloop()