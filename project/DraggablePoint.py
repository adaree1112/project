class DraggablePoint:
    def __init__(self, coord, controller):
        self.x, self.y = coord
        self.controller = controller
        self.artist = None
        self.press = None

        self.initial_x, self.initial_y = coord

    # ... (on_press, on_motion, get_coords methods remain largely the same)
    def connect(self):
        fig = self.artist.figure
        self.cidpress = fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.artist.axes:
            return
        contains, _ = self.artist.contains(event)
        if not contains:
            return
        x0, y0 = self.artist.get_data()
        self.press = (x0[0], y0[0]), (event.xdata, event.ydata)

    def attach(self, ax):
        # Re-attach logic for a point that might have been moved
        self.artist, = ax.plot(self.x, self.y, 'ro', picker=5)
        self.connect()

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.artist.axes:
            return
        (x0, y0), (xpress, ypress) = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        self.x = x0 + dx
        self.y = max(y0 + dy, 0)
        self.artist.set_data([self.x], [self.y])
        self.artist.figure.canvas.draw()

    def on_release(self, event):
        if self.press is None:
            return
        self.press = None
        self.artist.figure.canvas.draw_idle()

        old_x, old_y = self.initial_x, self.initial_y
        new_x, new_y = self.x, self.y

        self.initial_x, self.initial_y = new_x, new_y

        self.controller.point_moved(old_x, old_y, new_x, new_y)

    def get_coords(self):
        return self.x, self.y