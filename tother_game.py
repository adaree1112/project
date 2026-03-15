import tkinter as tk
from PIL import Image, ImageTk
from random import shuffle

from the_game import ButtonsFrame


class TOtherGameModel:
    def __init__(self):
        self.card_ranks = {v: i for i, v in enumerate("23456789TJQKA")}
        self.score = 0
        self.run = 0
        self.max_run = 0
        self.deck = None

        self.prev_card = ""
        self.new_game()

    def new_game(self):
        self.score = 0
        self.run = 0
        deck = [[f"{c}{s}" for c in "23456789TJQKA"] for s in "SHDC"]
        deck = deck[0] + deck[1] + deck[2] + deck[3]
        shuffle(deck)
        self.deck = iter(deck)

    def get_next_card(self, guess=""):
        try:
            card = next(self.deck)
        except StopIteration:
            return None
        if self.prev_card == "":
            self.prev_card = card
            return card, {"Score": self.score, "Run": self.run, "Max Run": self.max_run}
        correct = ""
        if self.card_ranks[self.prev_card[0]] < self.card_ranks[card[0]]:
            correct = "H"
        elif self.card_ranks[self.prev_card[0]] > self.card_ranks[card[0]]:
            correct = "L"

        if correct == "":
            self.run += 1

        elif correct == guess:
            self.run += 1
            self.score += 1
        else:
            self.run = 0

        if self.run > self.max_run:
            self.max_run = self.run

        self.prev_card = card
        return card, {"Score": self.score, "Run": self.run, "Max Run": self.max_run}


class TOtherGameController:
    def __init__(self, view):
        self.view = view
        self.model = TOtherGameModel()
        self.initialise_view()
        self.view.set_buttons({"Start": self.game_phase,
                               "Higher": lambda: self.view.update_card_screen(self.model.get_next_card("H"),
                                                                              self.restart_callback),
                               "Lower": lambda: self.view.update_card_screen(self.model.get_next_card("L"),
                                                                             self.restart_callback), })
        self.start_phase()

    def initialise_view(self):
        self.view.master.bind("<Escape>", self.restart_callback)

    def start_phase(self):
        self.view.configure_start_phase()

    def game_phase(self):
        self.view.configure_game_phase()
        self.view.update_card_screen(self.model.get_next_card())

    def restart_callback(self, _event=None):
        self.model.new_game()
        self.start_phase()


def blank_image() -> tk.PhotoImage:
    return ImageTk.PhotoImage(Image.new('RGBA', (250, 350), (0, 0, 0, 0)))


class ScoreFrame(tk.Frame):
    def __init__(self, master, text, num):
        super().__init__(master)
        self.text = tk.Label(self, text=text, font="(Ariel,20)")
        self.num = tk.Label(self, text=num, font="(Ariel,20)")

        self.text.grid(column=0, row=0)
        self.num.grid(column=0, row=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


class ScoresFrame(tk.Frame):
    def __init__(self, master, scores_dict):
        super().__init__(master)

        for i, (text, values) in enumerate(scores_dict.items()):
            ScoreFrame(self, text, values).grid(column=i, row=0)
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)


class TOtherGameView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.buttons = None
        self.card_image_dict = {}

        self.blank_image = blank_image()

        self.scores_frame = ScoresFrame(self, {"Score": 0, "Run": 0, "Max Run": 0})
        self.card_label = tk.Label(self, anchor="center", image=self.blank_image)

    def set_buttons(self, button_dict):
        self.buttons = ButtonsFrame(self, button_dict)
        self.place_widgets()

    def place_widgets(self):
        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.scores_frame.grid(column=0, row=0, sticky="nsew")
        self.card_label.grid(row=1, column=0)
        if self.buttons is not None:
            self.buttons.grid(row=2, column=0, sticky="nsew")

    def update_scores_frame(self, scores_dict):
        self.scores_frame.destroy()
        self.scores_frame = ScoresFrame(self, scores_dict)
        self.scores_frame.grid(column=0, row=0, sticky="nsew")

    def configure_start_phase(self):
        self.buttons.enable_button("Start")
        self.buttons.disable_button("Higher")
        self.buttons.disable_button("Lower")
        self.card_label["image"] = self.blank_image

    def configure_game_phase(self):
        self.buttons.disable_button("Start")
        self.buttons.enable_button("Higher")
        self.buttons.enable_button("Lower")

    def update_card_screen(self, card_and_scores, restart_callback=None):
        if card_and_scores is None:
            restart_callback()
            return
        card, scores = card_and_scores
        if card not in self.card_image_dict:
            size = (250, 350)
            image = Image.open(f'assets/cards/{card}.png').resize(size, Image.Resampling.LANCZOS).convert("RGBA")
            self.card_image_dict[card] = ImageTk.PhotoImage(image)
        self.update_scores_frame(scores)
        self.card_label['image'] = self.card_image_dict[card]


if __name__ == "__main__":
    root = tk.Tk()
    tview = TOtherGameView(root)
    controller = TOtherGameController(tview)
    tview.pack(expand=True, fill='both')
    root.resizable(False, False)
    root.geometry("300x500")
    root.mainloop()
