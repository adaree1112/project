import matplotlib
matplotlib.use('Agg')
import io
from PIL import Image, ImageTk
import matplotlib.pyplot as plt


def latex_to_tk_image(latex_str: str, fontsize: int = 10) -> ImageTk.PhotoImage:
    fig = plt.figure(figsize=(2, 2))
    fig.text(0, 0, latex_str, fontsize=fontsize,verticalalignment='top')
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", pad_inches=0.1,facecolor='#F0F0ED')
    plt.close(fig)
    buf.seek(0)
    return ImageTk.PhotoImage(Image.open(buf))