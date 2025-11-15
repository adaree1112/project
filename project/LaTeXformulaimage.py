import io
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt


def latex_to_tk_image(latex_str: str, fontsize: int = 20) -> ImageTk.PhotoImage:
    fig = plt.figure(figsize=(2, 2))
    fig.text(0, 0, latex_str, fontsize=fontsize)
    fig.savefig("latex.png", format="png", dpi=150, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return ImageTk.PhotoImage(Image.open("latex.png"))




# Example usage
root = tk.Tk()
latex_img = latex_to_tk_image(r"$X \sim \text{B}(n, p)$")
label = tk.Label(root, image=latex_img)
label.pack()
root.mainloop()