import matplotlib

matplotlib.use('Agg')
import io
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import tkinter as tk


def latex_to_tk_image(latex_str: str, fontsize: int = 10) -> tk.PhotoImage:
    """
    Converts a LaTeX string into a Tkinter-compatible image

    This function uses Matplotlib to render the LaTeX string into an image, and then converts it to a PhotoImage that Tkinter can display

    Parameters
    ----------
    latex_str : str
        The LaTeX string to be converted
    fontsize : int,
        The font size for the rendered LaTeX string.
        Default is 10

    Returns
    -------
    tk.PhotoImage
        The Tkinter-compatible image object created from the LaTeX string.
    """
    fig = plt.figure(figsize=(2, 2))
    fig.text(0, 0, latex_str, fontsize=fontsize, verticalalignment='top')
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", pad_inches=0.1, facecolor='#F0F0ED')
    plt.close(fig)
    buf.seek(0)
    return ImageTk.PhotoImage(Image.open(buf))
