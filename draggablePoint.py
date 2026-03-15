import matplotlib.axes
import matplotlib.backend_bases


class DraggablePoint:
    """
    A class to create a draggable point on a plot

    Attributes
    ----------
    x:float
        The x-coordinate of the point
    y:float
        The y-coordinate of the point
    controller : object
        The controller object that will handle the movement of the point
    artist : matplotlib.artist.Artist
        The artist object representing the draggable point
    press : tuple
        The initial position when the drag starts, followed by the current mouse position.
        Stored as ((x0,y0),(x_press, y_press),
        Where (x_press,y_press) are the current mouse coordinates
    initial_x : float
        The initial x-coordinate of the point
    initial_y : float
        The initial y-coordinate of the point
    """

    def __init__(self, coord: tuple[float | int, float | int], controller: object) -> None:
        """
        Constructs the required attributes for the draggable point

        Parameters
        ----------
        coord : tuple[float|int,float|int]
            A tuple (x,y) representing the initial coordinates of the point
        controller : object
            The controller object that will handle the movement of the point
        """
        self.x, self.y = coord
        self.controller = controller
        self.artist = None
        self.press = None

        self.initial_x, self.initial_y = coord

    def connect(self) -> None:
        """
        Connects the event handlers for mouse press, mouse release and motion events.

        This establishes connections to the corresponding events in order to drag the points on the plot.
        """

        fig = self.artist.figure

        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('button_release_event', self.on_release)
        fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Handles the mouse press event to begin dragging the point.

        Parameters
        ----------
        event : matplotlib.backend_bases.MouseEvent
            The mouse event that triggered the mouse press.

        Returns
        -------
        None:
            If the mouse event is outside teh axes or the point is not selected
        """
        if event.inaxes != self.artist.axes:
            return
        contains, _ = self.artist.contains(event)
        if not contains:
            return
        x0, y0 = self.artist.get_data()
        self.press = (x0[0], y0[0]), (event.xdata, event.ydata)

    def attach(self, ax: matplotlib.axes.Axes) -> None:
        """
        Attaches the draggable point to the given axes
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes on which to attach the draggable point
        """
        self.artist, = ax.plot(self.x, self.y, 'ro', picker=5)
        self.connect()

    def on_motion(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Handles the mouse motion event to update the position of the point.

        Parameters
        ----------
        event : matplotlib.backend_bases.MouseEvent
            The mouse event that triggered the mouse motion.

        Returns
        -------
        None
            If the press has not yet occurred of if the even is outside the axes.
        """
        if self.press is None or event.inaxes != self.artist.axes:
            return
        (x0, y0), (x_press, y_press) = self.press
        dx = event.xdata - x_press
        dy = event.ydata - y_press

        self.x = x0 + dx
        self.y = max(y0 + dy, 0)
        self.artist.set_data([self.x], [self.y])
        self.artist.figure.canvas.draw()

    def on_release(self, _event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Handles the mouse release event to update the position of the point.

        Parameters
        ----------
        _event : matplotlib.backend_bases.MouseEvent
            The mouse event that triggered the mouse release

        Returns
        -------
        None
            If the press has not yet occurred
        """

        if self.press is None:
            return
        self.press = None
        self.artist.figure.canvas.draw_idle()

        old_x, old_y = self.initial_x, self.initial_y
        new_x, new_y = self.x, self.y

        self.initial_x, self.initial_y = new_x, new_y
        if hasattr(self.controller, 'point_moved'):
            self.controller.point_moved(old_x, old_y, new_x, new_y)

    def get_coords(self) -> tuple[float, float]:
        """
        Returns the current x,y coordinates of the point.

        Returns
        -------
        tuple[float, float]
            A tuple (x,y) representing the current x,y coordinates of the point.
        """
        return self.x, self.y
