import random

import numpy as np
import math
from scipy.special import comb,gamma,gammainc

from fittingFunctions import piecewise_cubic_spline, piecewise_linear, merge_sort


def integrate_nbic(x1: float, x2: float, a: float, b: float, c: float, d: float, n: int) -> float:
    """
    Compute the definite integral of a polynomial of order n with 4 terms:
    P(x) = a*x^n + b*x^(n-1) + c*x^(n-2) + d*x^(n-3) over [A, B].

    Parameters
    ----------
    x1 : float
        Lower bound of the integral.
    x2 : float
        Upper bound of the integral.
    a : float
        Coefficient of x^n.
    b : float
        Coefficient of x^(n-1).
    c : float
        Coefficient of x^(n-2).
    d : float
        Coefficient of x^(n-3).
    n : int
        Order of the polynomial (must be > 2).

    Returns
    -------
    float
        The definite integral of the polynomial from `A` to `B`.
    """
    return a * (x2 ** (n + 1) - x1 ** (n + 1)) / (n + 1) + b * (x2 ** n - x1 ** n) / n + c * (
            x2 ** (n - 1) - x1 ** (n - 1)) / (n - 1) + d * (x2 ** (n - 2) - x1 ** (n - 2)) / (n - 2)


def binary_search_for_x(target_p:float, minimum:float, maximum:float, func:callable) ->float|None:
    """
    Find the approximate x value such that func(x) is sufficiently close to target_p using binary search.

    Returns None if no value is found
    Parameters
    ----------
     target_p : float
        The value we want func(x) to be approximately equal to.
    minimum : float
        The lower bound of the search interval.
    maximum : float
        The upper bound of the search interval.
    func :
        An increasing function.

    Returns
    -------
    float
        A value x in [minimum, maximum] such that func(x) ≈ target_p
    """
    middle = (minimum + maximum) / 2
    if np.isclose(func(middle), target_p, atol=1e-10):
        return middle
    if func(middle) < target_p:
        return binary_search_for_x(target_p, middle, maximum, func)
    elif func(middle) > target_p:
        return binary_search_for_x(target_p, minimum, middle, func)
    return None

def mean(l:list) -> float:
    """
    Return the arithmetic mean of a list of values
    Parameters
    ----------
    l : list
        The list of values.

    Returns
    -------
    float
        The arithmetic mean of the list of values.
    """
    if len(l)==0:
        return -1
    return sum(l)/len(l)

def sample_var(l:list)->float:
    """
    Return the sample variance of a list of values.
    Parameters
    ----------
    l : list
        The list of values.

    Returns
    -------
    float
        The sample variance of the list of values.
    """
    try:
        x_bar=mean(l)
        return sum((x-x_bar)**2 for x in l)/(len(l)-1)
    except ZeroDivisionError:
        return -1

def count_multiple(l:list, value_list:list)->int:
    """
    Count the number of times a value from `value_list` appears in `l`.
    Parameters
    ----------
    l : list
        The list of values to check
    value_list : list
        The list of values to check for.

    Returns
    -------
    int
        the number of times a value appears in `value_list` appears in `l`.
    """
    return sum(l.count(value) for value in value_list)

def count_less_than_equal_to(l:list, x:float)->int:
    """
    Count the number of times a value from `l` is less than or equal to `x`.
    Parameters
    ----------
    l : list
        The list of values.
    x : float
        The value to check for values less than or equal to

    Returns
    -------
    int
        the number of times a value appears in `l` is less than or equal to `x`.
    """
    return sum([1 for i in l if i<=x])

class Piecewise:
    """
    Probability distribution based of Piecewise Function

    Represents a function defined by a set of (x, y) points,
    interpolated using either piecewise cubic splines or piecewise linear
    segments. It supports normalisation, integration, expectation,
    variance, and cumulative distribution–like queries.

    Parameters
    ----------
    points : list of tuple of float
        List of (x, y) points defining the function.

    Attributes
    ----------
    is_discrete : bool
        Indicates whether the distribution is discrete (always False here).
    _points : list of tuple of float
        List of (x, y) points defining the function.
    is_normalised : bool
        Indicates whether the distribution is normalised.
    pieces : list
        A list containing (x1,x2,a,b,c,d) representing the polynomial ax^3 + bx^2 + cx + d in the range [x1,x2]
    """

    def __init__(self, points:list[tuple[float, float]]) -> None:
        """
        Initialise the Piecewise object.

        Parameters
        ----------
        points : list of tuple of float
            Initial control points defining the function.
        """
        self.is_discrete = False
        self._points = points
        self.is_normalised = False
        self.pieces = []
        self.calculate_pieces()

    @property
    def mini(self)->float:
        """
        Minimum x-value among control points.

        Returns
        -------
        float
            Minimum x-coordinate.
        """
        x, y = zip(*self._points)
        return min(x)

    @property
    def maxi(self)->float:
        """
        Maximum x-value among control points.

        Returns
        -------
        float
            Maximum x-coordinate.
        """
        x, y = zip(*self._points)
        return max(x)

    def get_points(self)->list[tuple[float, float]]:
        """
        Return the list of control points.

        Returns
        -------
        list of tuple of float
            The (x, y) control points.
        """
        return self._points

    def get_num_points(self) ->int:
        """
        Return the number of control points.

        Returns
        -------
        int
            Number of points.
        """
        return len(self._points)

    def check_for_point(self,point:tuple)->tuple[float, float]|bool:
        """
        Check if there is a point at the specified location. Return True if yes.

        Parameters
        ----------
        point: tuple of float
            point x and y coordinates to check.

        Returns
        -------
        tuple[float, float]
            the point that exists if a point exists.

        False if not.
        """
        offset=(self.maxi-self.mini)/10
        for pt in self._points:
            if abs(point[0] - pt[0]) < offset and abs(point[1] - pt[1]) < offset:
                return pt
        return False

    def add_point(self, point : None|tuple[float,float] = None) -> None:
        """
        Add a control point to the Piecewise object.

        If a point is provided, add that point to the list of control points.
        Otherwise, add a control point from within the current range of x and y values
        If a point is already in that location, remove it
        Normalisation state is reset to false.

        Parameters
        ----------
        point : tuple of float, optional
            A specific (x, y) point to add.
        """
        self.is_normalised = False

        if point is None:
            if not self._points:
                self._points+=[(0, 0), (1, 1)]
            elif len(self._points) < 2:
                if self._points[0] != (1, 1):
                    self._points.append((1, 1))
                else:
                    self._points.append((0, 0))
            else:
                curr_x, curr_y = zip(*self._points)
                new_x = random.uniform(min(curr_x), max(curr_x))
                new_y = random.uniform(0, max(curr_y))
                self._points.append((new_x, new_y))
        else:
            if pt:=self.check_for_point(point):
                self.remove_point(pt)
            else:
                self._points.append(point)


    def remove_point(self,point=None)->None:
        """
        Remove a random control point.

        Only removes a point if more than two points exist.
        Normalisation state is reset to False.
        """
        self.is_normalised = False
        if len(self._points) > 2:
            if point is None:
                self._points.pop(random.randint(0, len(self._points) - 1))
            else:
                self._points.remove(point)


    def calculate_pieces(self, linear:bool=False)->None:
        """
        Recompute the piecewise representation.

        Parameters
        ----------
        linear : bool, optional
            If True, use piecewise linear interpolation.
            If False, use cubic spline interpolation.
        """
        sorted_points = merge_sort(self._points, key=lambda p: p[0])
        if not linear:
            self.pieces = piecewise_cubic_spline(sorted_points)
        else:
            self.pieces = piecewise_linear(sorted_points)

    def update_point(self, old_x:float, old_y:float, new_x:float, new_y:float)->None:
        """
        Update an existing control point.

        First matching point (only) will always be updated.
        Normalisation state is reset to False.

        Parameters
        ----------
        old_x:float
            Original x-coordinate.
        old_y:float
            Original y-coordinate.
        new_x:float
            New x-coordinate.
        new_y:float
            New y-coordinate.
        """
        for i, (x, y) in enumerate(self._points):
            if np.isclose(x, old_x) and np.isclose(y, old_y):
                self._points[i] = (new_x, new_y)
                self.is_normalised = False
                break

    def normalise(self):
        """
        Normalise the function so that the total area equals 1.

        Scales both control points and piecewise coefficients.
        Normalisation state set to True.
        """
        area = self.integrate_piecewise()
        k = 1 / area
        self._points = [(point[0], k * point[1]) for point in self._points]
        self.pieces = [np.concatenate((piece[:2], k * piece[2:])) for piece in self.pieces]
        self.is_normalised = True

    def integrate_piecewise(self, l : float | None = None, u : float | None = None)->float:
        """
        Integrate the piecewise function over a given interval.

        If no bounds are given, or a bound is missing, it treats it as ±∞, by integrating over the full range of the piecewise function, mini to maxi

        Parameters
        ----------
        l : float, optional
            Lower integration bound.
        u : float, optional
            Upper integration bound.

        Returns
        -------
        float
            Definite integral over the specified interval.
        """
        total = 0
        for p, piece in enumerate(self.pieces):
            x1, x2, a, b, c, d = piece

            lower_bound = x1
            upper_bound = x2
            if l is not None:
                lower_bound = max(l, x1)
            if u is not None:
                upper_bound = min(u, x2)

            if lower_bound < upper_bound:
                total += integrate_nbic(lower_bound, upper_bound, a, b, c, d, 3)
        return total

    def expectation(self, sq:bool=False)->float:
        """
        Compute the expected value, E(X) or the expected value of x^2, E(X²)

        Parameters
        ----------
        sq : bool, optional
            If True, compute the Expected Value of X^2
            If False, compute the Expected Value of X

        Returns
        -------
        float
            The expected value.

        """
        total = 0
        for piece in self.pieces:
            x1, x2, a, b, c, d = piece
            total += integrate_nbic(x1, x2, a, b, c, d, 4 + sq)
        return total

    def variance(self) -> float:
        """
        Compute the variance of the piecewise function

        This uses the formula Var(X) = E(X²) - E(X)²

        Returns
        -------
        float
            The variance.

        """
        return self.expectation(sq=True) - self.expectation() ** 2

    def cdf(self, x_vals:int|float | np.ndarray[np.float64])->float|np.ndarray:
        """
        Compute the cumulative distribution function, P(X ≤ x).

        If there are multiple `x_vals` then compute for each

        Parameters
        ----------
        x_vals : int, float or ndarray
            Input x-value(s).

        Returns
        -------
        float or array of float
            CDF value(s).
        """
        if self.is_normalised:
            if isinstance(x_vals, np.ndarray):
                return np.array([self.pxlessthan(x) for x in x_vals])
            else:
                return self.pxlessthan(x_vals)
        return 0

    def pxlessthan(self, x:float)->float:
        """
        If Normalised, Compute P(X<x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
            return self.integrate_piecewise(u=x)
        return 0

    @staticmethod
    def pxequals(x:float)->float:
        """
        Compute P(X=x)

        Always equals 0, as continuous distribution.

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if x:
            return 0
        return 0

    def pxlessthanequalto(self, x:float)->float:
        """
        If Normalised, Compute P(X≤x)

        This is identical to pxlessthan as the distribution is continuous.

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
           return self.pxlessthan(x)
        return 0

    def pxgreaterthan(self, x:float)->float:
        """
        If Normalised, Compute P(X>x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
            return 1 - self.pxlessthan(x)
        return 0

    def pxgreaterthanequalto(self, x:float)->float:
        """
        If Normalised, Compute P(X≥x)

        This is identical to pxgreaterthan as the distribution is continuous.

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
            return self.pxgreaterthan(x)
        return 0

    def pxinclusivein(self, a:float, b:float)->float:
        """
        If Normalised, Compute P(a≤X≤b)

        Parameters
        ----------
        a:float
        b:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
            return self.pxlessthan(b) - self.pxlessthan(a)
        return 0

    def pxexclusivein(self, a:float, b:float)->float:
        """
        If Normalised, Compute P(a<X<b)

        This is identical to pxinclusivein as the distribution is continuous.

        Parameters
        ----------
        a:float
        b:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_normalised:
            return self.pxinclusivein(a, b)
        return 0

    # FIND x from p
    def xplessthan(self, p:float)->float:
        """
        If Normalised, Compute x such that P(X<x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_normalised:
            xs = [pt[0] for pt in self._points]
            return binary_search_for_x(p, min(xs), max(xs), self.pxlessthan)
        return 0

    def xplessthanequalto(self, p:float)->float:
        """
        If Normalised, Compute x such that P(X≤x)=p

        This is identical to xplessthan as the distribution is continuous.

        Parameters
        ----------
        p : float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_normalised:
            return self.xplessthan(p)
        return 0

    def xpgreaterthan(self, p:float)->float:
        """
        If Normalised, Compute x such that P(X>x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_normalised:
            return self.xplessthan(1 - p)
        return 0

    def xpgreaterthanequalto(self, p:float)->float:
        """
        If Normalised, Compute x such that P(X≥x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_normalised:
            return self.xpgreaterthan(p)
        return 0

    def xpinclusivein(self, p:float)->float:
        """
        Find interval containing probability p (inclusive).

        Parameters
        ----------
        p:float

        Raises
        ------
        NotImplementedError
            This is not implemented for Piecewise distributions.
        """
        raise NotImplementedError

    def xpexclusivein(self, p:float)->float:
        """
        Find interval containing probability p (exclusive).

        Parameters
        ----------
        p:float

        Raises
        ------
        NotImplementedError
            This is not implemented for Piecewise distributions.
        """
        raise NotImplementedError


class AbstractStatisticalModel:
    """
    Abstract base class for statistical models (discrete or continuous).

    Attributes
    ----------
    parameters : dict
        Dictionary storing the model parameters.
    is_discrete : bool
        Flag indicating if the distribution is discrete.
    """
    def __init__(self, parameters:dict[str:'Parameter'], is_discrete:bool)->None:
        """
        Initialise the statistical model with parameters and type.

        Parameters
        ----------
        parameters : dict
            Distribution-specific parameters.
        is_discrete : bool
            True if distribution is discrete, False if continuous.
        """
        self.parameters = parameters
        self.is_discrete = is_discrete

    @property
    def mini(self)->float|int:
        """
        Minimum value of the distribution.

        Returns
        -------
        float or int
            Lower bound of the distribution.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError

    @property
    def maxi(self)->float|int:
        """
        Maximum value of the distribution.

        Returns
        -------
        float or int
            Upper bound of the distribution.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError

    def pdf(self, x:float|np.ndarray)->float|np.ndarray:
        """
        Probability density function (PDF) for continuous or probability mass function (PMF) for discrete.

        Parameters
        ----------
        x : float, or np.ndarray
            Value(s) at which to evaluate the probability.

        Returns
        -------
        float or np.ndarray
            Probability value(s) at `x`.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError

    def get_plot_data(self)->tuple[np.ndarray, np.ndarray,str,callable]:
        """
        Generate graph data for plotting the distribution.

        For discrete distributions, returns bar data.
        For continuous distributions, returns line data.

        Returns
        -------
        x_vals : np.ndarray
            Array of x-values for plotting.
        y_vals : np.ndarray
            Corresponding probabilities or densities.
        graphtype : str
            'bar' for discrete, 'line' for continuous.
        pxlessthanequalto : callable
            Method to calculate cumulative probabilities up to a value.
        """
        if self.is_discrete:
            x_vals = np.arange(self.mini, self.maxi + 1)
            y_vals = self.pdf(x_vals)
            graphtype = 'bar'
        else:
            x_vals = np.linspace(self.mini, self.maxi, 100)
            y_vals = self.pdf(x_vals)
            graphtype = 'line'
        return x_vals, y_vals, graphtype, self.pxlessthanequalto

    def get_parameters(self)->dict[str:'Parameter']:
        """
        Get the parameters of the distribution.

        Returns
        -------
        dict
            Distribution parameters as a dictionary of `Parameter` objects.
        """
        return self.parameters

    def cdf(self, x: float | int | np.float64 | np.ndarray)-> float|np.ndarray:
        """
        Cumulative distribution function (CDF).

        Parameters
        ----------
        x: float, int, np.float64 or np.ndarray
            Value(s) at which to evaluate the cumulative distribution function.

        Returns
        -------
        float or np.ndarray of floats
            Cumulative Probability Value(s) at `x` value(s)
        """
        if isinstance(x, np.ndarray):
            return np.array([self.cdf(c) for c in x])
        total = 0.0

        if self.is_discrete:
            total = 0.0
            for i in range(int(self.mini), int(x) + 1):
                total += self.pdf(i)
        else:
            n = 1000
            h = float(x - self.mini) / n
            total += self.pdf(self.mini) / 2.0
            for i in range(1, n):
                total += self.pdf(self.mini + i * h)
            total += self.pdf(x) / 2.0
            total *= h
        return total

    ##FIND p from x
    def pxequals(self, x:float)->float:
        """
        Compute P(X=x)

        Always equals 0 for continuous distributions.

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_discrete:
            if self.mini <= x <= self.maxi:
                return self.pdf(x)
        return 0

    def pxlessthan(self, x:float)->float:
        """
        Compute P(X<x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.mini <= x:
            if self.is_discrete:
                return self.cdf(min(x - 1, self.maxi))
            else:
                return self.cdf(min(x, self.maxi))
        return 0

    def pxlessthanequalto(self, x:float)->float:
        """
        Compute P(X≤x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_discrete:
            return self.pxlessthan(x + 1)
        else:
            return self.pxlessthan(x)

    def pxgreaterthan(self, x:float)->float:
        """
        Compute P(X>x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        return 1 - self.pxlessthanequalto(x)

    def pxgreaterthanequalto(self, x:float)->float:
        """
        Compute P(X≥x)

        Parameters
        ----------
        x:float

        Returns
        -------
        float
            Probability value
        """
        return 1 - self.pxlessthan(x)

    def pxinclusivein(self, a:float, b:float)->float:
        """
        Compute P(a≤X≤b)

        Parameters
        ----------
        a:float
        b:float

        Returns
        -------
        float
            Probability value
        """
        if self.is_discrete:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a - 1)
        else:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a)

    def pxexclusivein(self, a:float, b:float)->float:
        """
        Compute P(a<X<b)

        Parameters
        ----------
        a:float
        b:float

        Returns
        -------
        float
            Probability value
        """
        return self.pxlessthan(b) - self.pxlessthan(a)

    # FIND p from x
    def xplessthan(self, p:float)->float:
        """
        Compute x such that P(X<x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_discrete:
            prev_x = None
            for x in range(self.mini, self.maxi + 1):
                if self.pxlessthan(x) <= p:
                    prev_x = x
                else:
                    break
            return prev_x
        else:
            return binary_search_for_x(p, self.mini, self.maxi, self.pxlessthan)

    def xplessthanequalto(self, p:float)->float:
        """
        Compute x such that P(X≤x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_discrete:
            prev_x = None
            for x in range(self.mini, self.maxi + 1):
                if self.pxlessthanequalto(x) <= p:
                    prev_x = x
                else:
                    break
            return prev_x
        else:
            return binary_search_for_x(p, self.mini, self.maxi, self.pxlessthan)

    def xpgreaterthan(self, p:float)->float:
        """
        Compute x such that P(X>x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_discrete:
            prev_x = None
            for x in range(self.maxi, self.mini - 1, -1):
                if self.pxgreaterthan(x) <= p:
                    prev_x = x
                else:
                    break
            return prev_x
        else:
            return binary_search_for_x(p, self.maxi, self.mini, self.pxgreaterthan)

    def xpgreaterthanequalto(self, p:float)->float:
        """
        Compute x such that P(X≥x)=p

        Parameters
        ----------
        p:float

        Returns
        -------
        float
            Corresponding x-value.
        """
        if self.is_discrete:
            prev_x = None
            for x in range(self.maxi, self.mini - 1, -1):
                if self.pxgreaterthanequalto(x) <= p:
                    prev_x = x
                else:
                    break
            return prev_x
        else:
            return binary_search_for_x(p, self.maxi, self.mini, self.pxgreaterthan)

    def xpinclusivein(self, p:float)->tuple[float,float]:
        """
        Compute a such that P(μ-a≤X≤μ+a)=p

        Where μ is the mean.

        Parameters
        ----------
        p : float
            Target probability.

        Returns
        -------
        tuple of floats
            μ-a,μ+a

        Raises
        ------
        NotImplementedError
            Only implemented for normal distribution as must be symmetrical
        """
        raise NotImplementedError

    def xpexclusivein(self, p:float)->tuple[float,float]:
        """
        Compute a such that P(μ-a<X<μ+a)=p

        Where μ is the mean.

        Parameters
        ----------
        p : float
            Target probability.

        Returns
        -------
        tuple of floats
            μ-a,μ+a

        Raises
        ------
        NotImplementedError
            Only implemented for normal distribution as must be symmetrical
        """
        raise NotImplementedError

    def expectation(self)->float:
        """
        Expected value (mean) of the distribution.

        Returns
        -------
        float
            E(X)

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError

    def variance(self)->float:
        """
        Variance of the distribution.

        Returns
        -------
        float
            Var(X)

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError


class Normal(AbstractStatisticalModel):
    """
    Represents a Normal distribution.

    Attributes:
    -----------
    parameters : dict
        Dictionary containing 'mu' (mean) and 'sigma' (standard deviation).
    """
    def __init__(self, parameters:dict=None)->None:
        """
        Initialise a Normal distribution with given parameters.
        Parameters
        ----------
        parameters: dict
            Dictionary containing 'mu' (mean) and 'sigma' (standard deviation).
        """
        super().__init__(parameters, False)

    def pdf(self, x:float|np.ndarray)->float|np.ndarray:
        """
        Probability density function of the normal distribution.
        Parameters
        ----------
        x : float or np.ndarray
            Point(s) at which to evaluate the PDF.

        Returns
        -------
        float or np.ndarray
            Value of the PDF at `x`.
        """
        mu = self.parameters["mu"].value
        sigma = self.parameters["sigma"].value
        return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

    @property
    def mini(self)->float:
        """
        Lower bound for plotting or searching, 5 standard deviations below mean.

        Returns
        -------
        float
        """
        return self.expectation() - 5 * self.variance() ** .5

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, 5 standard deviations above mean.

        Returns
        -------
        float
        """
        return self.expectation() + 5 * self.variance() ** .5

    def expectation(self)->float:
        """
        Mean (expected value) of the normal distribution.

        Returns
        -------
        float
        """
        mu = self.parameters["mu"].value
        return mu

    def variance(self)->float:
        """
        Variance of the normal distribution.

        Returns
        -------
        float
        """
        sigma = self.parameters["sigma"].value
        return sigma ** 2

    def xpexclusivein(self, p:float)->tuple[float,float]:
        """
        Returns the symmetric interval around the mean containing probability p.
        Parameters
        ----------
        p: float
            Target probability.

        Returns
        -------
        tuple of floats
            Lower and upper bounds of the interval.
        """

        mu = self.parameters["mu"].value

        def xbetweenmuandx(x):
            return self.cdf(x) - self.pxlessthan(mu)

        distance_from_mean = binary_search_for_x(p / 2, self.mini, self.maxi, xbetweenmuandx) - mu
        return mu - distance_from_mean, mu + distance_from_mean

    def xpinclusivein(self, p:float)->tuple[float,float]:
        """
        Returns the symmetric interval around the mean containing probability `p`.

        Parameters
        ----------
        p : float
            Probability mass to include in the interval.

        Returns
        -------
        tuple of float
            Lower and upper bounds of the interval.
        """
        return self.xpexclusivein(p)


class Binomial(AbstractStatisticalModel):
    """
    Represents a Binomial distribution.

    Attributes:
    -----------
    parameters : dict
        Dictionary containing 'n' (number of trials) and 'p' (success probability).
    """

    def __init__(self, parameters:dict=None)->None:
        """
        Initialise a Binomial distribution with given parameters.
        Parameters
        ----------
        parameters: dict
            Dictionary containing 'n' (number of trials) and 'p' (success probability).
        """
        super().__init__(parameters, True)

    @property
    def mini(self)->float:
        """
        Lower bound for plotting or searching, 0.

        Returns
        -------
        float
        """
        return 0

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, n.

        Returns
        -------
        float
        """
        return int(self.parameters["n"].value)

    def pdf(self, x:int|np.ndarray)->float|np.ndarray:
        """
        Probability mass function of the binomial distribution.

        Parameters
        ----------
        x : int or np.ndarray
            Number of successes.

        Returns
        -------
        float or np.ndarray
            Probability of x successes.
        """
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return comb(n, x) * (p ** x) * ((1 - p) ** (n - x))

    def expectation(self) -> float:
        """
        Mean (expected value) of the binomial distribution.

        Returns
        -------
        float
        """
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return n * p

    def variance(self) -> float:
        """
        Variance of the binomial distribution.

        Returns
        -------
        float
        """
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return n * p * (1 - p)


class Poisson(AbstractStatisticalModel):
    """
    Represents a Binomial distribution.

    Attributes:
        parameters (dict): Dictionary containing 'lam' (average rate).
    """

    def __init__(self, parameters:dict=None)->None:
        """
        Initialise a Poisson distribution with given parameters.
        Parameters
        ----------
        parameters: dict
            Dictionary containing 'lam' (average rate).
        """
        super().__init__(parameters, True)

    @property
    def mini(self)->float:
        """
        Lower bound for plotting or searching, 0.

        Returns
        -------
        float
        """
        return 0

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, 5 standard deviations above mean.

        Returns
        -------
        float
        """
        return int(self.expectation() + 5 * self.variance() ** .5)

    def pdf(self, x:int|np.ndarray|np.float64)->float|np.ndarray:
        """
        Probability mass function of the poisson distribution.

        Parameters
        ----------
        x : int or np.ndarray or np.float64
            Number(s) of events.

        Returns
        -------
        float
            Probability of x events.
        """
        if isinstance(x, np.ndarray):
            return np.array([self.pdf(c) for c in x])
        if isinstance(x,np.float64):
            return self.pdf(int(x))
        lam = self.parameters["lambda"].value
        return np.exp(-lam) * lam ** x / math.factorial(x)

    def expectation(self) -> float:
        """
        Mean (expected value) of the poisson distribution.

        Returns
        -------
        float
        """
        lam = self.parameters["lambda"].value
        return lam

    def variance(self) -> float:
        """
        Variance of the poisson distribution.

        Returns
        -------
        float
        """
        lam = self.parameters["lambda"].value
        return lam


class Geometric(AbstractStatisticalModel):
    """
    Represents a Geometric distribution.

    Attributes:
        parameters (dict): Dictionary containing 'p' (success probability).
    """

    def __init__(self, parameters:dict=None)->None:
        """
        Initialise a Geometric distribution with given parameters.
        Parameters
        ----------
        parameters: dict
            Dictionary containing 'p' (success probability).
        """
        super().__init__(parameters, True)

    @property
    def mini(self)->float:
        """
        Lower bound for plotting or searching, 1.

        Returns
        -------
        float
        """
        return 1

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, 5 standard deviations above mean.

        Returns
        -------
        float
        """
        return int(self.expectation() + 5 * self.variance() ** .5)

    def pdf(self, x:int|np.ndarray)->float|np.ndarray:
        """
        Probability mass function of the geometric distribution.

        Parameters
        ----------
        x : int or np.ndarray
            Number of trials until success.

        Returns
        -------
        float or np.ndarray
            Probability of x trials until first success.
        """
        p = self.parameters["p"].value
        return (1 - p) ** (x - 1) * p

    def expectation(self) -> float:
        """
        Mean (expected value) of the geometric distribution.

        Returns
        -------
        float
        """
        p = self.parameters["p"].value
        return 1 / p

    def variance(self) -> float:
        """
        Variance of the geometric distribution.

        Returns
        -------
        float
        """
        p = self.parameters["p"].value
        return (1 - p) * p ** -2


class Exponential(AbstractStatisticalModel):
    """
    Represents an Exponential distribution.

    Attributes:
        parameters (dict): Dictionary containing 'lam' (average rate).
    """

    def __init__(self, parameters:dict=None)->None:
        """
        Initialise an Exponential distribution with given parameters.
        Parameters
        ----------
        parameters: dict
            Dictionary containing 'lam' (average rate).
        """
        super().__init__(parameters, False)

    @property
    def mini(self)->float:
        """
        Lower bound for plotting or searching,0.

        Returns
        -------
        float
        """
        return 0

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, 5 standard deviations above mean.

        Returns
        -------
        float
        """
        return self.expectation() + 5 * self.variance() ** .5

    def pdf(self, x:float|np.ndarray)->float|np.ndarray:
        """
        Probability density function of the exponential distribution.
        Parameters
        ----------
        x : float or np.ndarray
            Point(s) at which to evaluate the PDF.

        Returns
        -------
        float or np.ndarray
            Value of the PDF at `x`.
        """
        lam = self.parameters["lambda"].value
        return lam * np.exp(-lam * x)

    def cdf(self, x:float|np.ndarray)->float|np.ndarray:
        """
        Cumulative density function of the exponential distribution.
        Parameters
        ----------
        x : float or np.ndarray
            Point(s) at which to evaluate the CDF.

        Returns
        -------
        float or np.ndarray
            Value of the CDF at `x`.
        """
        lam = self.parameters["lambda"].value
        return 1 - np.exp(-lam * x)

    def expectation(self)->float:
        """
        Mean (expected value) of the exponential distribution.

        Returns
        -------
        float
        """
        lam = self.parameters["lambda"].value
        return 1 / lam

    def variance(self)->float:
        """
        Variance of the exponential distribution.

        Returns
        -------
        float
        """
        lam = self.parameters["lambda"].value
        return lam ** -2


class ChiSquared(AbstractStatisticalModel):
    """
    Represents a Chi-squared distribution.

    Attributes:
        parameters (dict): Dictionary containing 'nu' (Degrees of freedom).
    """
    def __init__(self, parameters:dict=None)->None:
        """
        Initialise a Chi-squared distribution with given parameters.
        Parameters
        ----------
        parameters : dict
            Dictionary containing 'nu' (Degrees of freedom).
        """
        super().__init__(parameters, False)

    @property
    def mini(self) -> float:
        """
        Lower bound for plotting or searching,0.
        Returns
        -------
        float
            0
        """
        return 0

    @property
    def maxi(self)->float:
        """
        Upper bound for plotting or searching, 5 standard deviations above mean.
        Returns
        -------
        float
            upper bound
        """
        return self.expectation() + 5 * self.variance() ** .5

    def pdf(self, x:float|np.ndarray)->float|np.ndarray:
        """
        Probability density function of the Chi-squared distribution.

        Parameters
        ----------
        x : float or np.ndarray
            Point(s) at which to evaluate the PDF.

        Returns
        -------
        float or np.ndarray
            Value(s) of the PDF at `x`.

        """
        k=self.parameters["nu"].value
        output = np.zeros_like(x)
        mask = x>0
        output[mask] = x[mask]**(k/2-1) * np.exp(-x[mask]/2)/2**(k/2)/gamma(k/2)
        return output

    def cdf(self,x:float|np.ndarray)->float|np.ndarray:
        """
        Cumulative density function of the Chi-squared distribution.

        Parameters
        ----------
        x : float or np.ndarray
            Point(s) at which to evaluate the CDF.

        Returns
        -------
        float or np.ndarray
            Value(s) of the CDF at `x`.
        """
        k=self.parameters["nu"].value
        return gammainc(k/2,x/2)

    def expectation(self)->float:
        """
        Mean (expected value) of the Chi-squared distribution.

        Returns
        -------
        Int
            Mean (expected value) of the Chi-squared distribution.
        """
        k=self.parameters["nu"].value
        return k

    def variance(self)->float:
        """
        Variance of the Chi-squared distribution.

        Returns
        -------
        int
            Variance of the Chi-squared distribution.
        """
        k=self.parameters["nu"].value
        return 2*k

class Parameter:
    """
    A numeric parameter with bounds, step size and default value.

    This value can be configured in the GUI (typically with spinboxes).
    When a value is updated it is validated to remain in the range.

    Attributes
    ----------
    label : str
        symbol/ ame of the parameter.
        this will be displayed
    minimum : float or int
        Minimum allowable value.
    maximum : float or int
        Maximum allowable value.
    step : float or int
        Increment step size for changing the value.
    default : float or int
        Default value of the parameter.
    _value : float or int
        Internal storage for the current value.

    """
    def __init__(self, label:str, minimum:float|int, maximum:float|int, step:float|int, default:float|int)->None:
        """
            Initialise a Parameter instance.

            Parameters
            ----------
            label : str
                Human-readable name of the parameter.
            minimum : float or int
                Minimum allowable value.
            maximum : float or int
                Maximum allowable value.
            step : float or int
                Increment step size for changing the value.
            default : float or int
                Default value for the parameter.
            """
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.default = default
        self._value = default

    @property
    def value(self):
        """
        Get the current value of the parameter.

        Returns
        -------
        float or int
            The current value.
        """
        return self._value

    @value.setter
    def value(self, value:float)->None:
        """
        Set the value of the parameter.

        The value is converted to a float and only stored as the new value if it lies within the bounds
        Invalid or out-of-range values are silently ignored
        Parameters
        ----------
        value : float
            New value to assign.

        Returns
        -------

        """
        try:
            v = float(value)
            if self.minimum <= v <= self.maximum:
                self._value = v
        except ValueError:
            pass

    def get_label(self)->str:
        """
        Get the label of the parameter to display.

        Append an equals sign

        Returns
        -------
        str
            A string that combines the label and an equals sign, to be displayed
        """
        return self.label + " = "

    def validate(self, value:float|str)->bool:
        """
        Validate a value against the parameter bounds.

        Parameters
        ----------
        value: float
            Value to validate

        Returns
        -------
        bool
            True if the value can be converted to a float that lies between the bounds, else False.
        """
        try:
            v = float(value)
            return self.minimum <= v <= self.maximum
        except ValueError:
            return False

    def get_spinbox_args(self)->dict:
        """
        Return keyword arguments for configuring the spinbox section of a LabelSpinbox widget.

        Returns
        -------
        dict
            Dictionary containing minimum,maximum,step, and arbitrary width setting.
        """
        return {"from_": self.minimum, "to": self.maximum, "increment": self.step, "width": 5}


class Die:
    """
    A standard D6 that can be rolled to generate a random value.

    Attributes
    ----------
    num : int
        The current face value of the die.
    """

    def __init__(self):
        """
        Initialise the die and roll it once.

        The die's initial value is set by calling 'roll()' during initialisation.
        """
        self.num = 0
        self.roll()

    def roll(self)->int:
        """
        Roll the die and update its value.

        Returns
        -------
        int
            A random integer between 1 and 6 (inclusive) representing the new value of the die.
        """
        self.num = random.randint(1, 6)
        return self.num


class AbstractDicetribution:
    """
    Abstract base class for dice-based probability distributions.

    Attributes
    ---------
    dice_data : list of lists of dice
        each sublist or row contains a set of dice which are later analysed.

    parameters : dict
        Dictionary containing 'num' (number of rows) and distribution specific parameters.
    """
    def __init__(self,parameters:dict=None)->None:
        """
        Initialise the distribution.

        Parameters
        ----------
        parameters : dict
            Dictionary containing 'num' (number of rows) and distribution specific parameters.
        """
        self.dice_data = []
        self.parameters = parameters
        self.set_n_dice_row(self.parameters["num"].value)

    def get_dice_row(self) -> list[Die]:
        """
        Create and return a single row of dice

        Returns
        -------
        list
            A list containing dice

        Raises
        ------
        NotImplementedError
            Must be implemented in subclasses.
        """
        raise NotImplementedError

    def get_row_data(self,row:list[Die])->float:
        """
        Perform a calculation on the row of dice to obtain a piece of data
        Parameters
        ----------
        row : list of dice
            The list to perform the calculation on.

        Returns
        -------
        float
            The piece of data calculated from the row of dice.
        """
        raise NotImplementedError

    def add_dice_row(self, n:int=1)->None:
        """
        Add one or more dice rows.

        If negative, rows are removed instead.
        Parameters
        ----------
        n : int
            Number of rows to add. 1 by default.
        """
        for _ in range(int(n)):
            self.dice_data.append(self.get_dice_row())
        if n<0:
            self.remove_dice_row(n=-n)

    def remove_dice_row(self, n:int=1)->None:
        """
        Remove one or more dice row from the end.

        Parameters
        ----------
        n : int
            Number of rows to remove. 1 by default.
        """
        for _ in range(int(n)):
            self.dice_data.pop()

    def set_n_dice_row(self, n:int)->None:
        """
        Remove all dice rows and add the required number of dice rows.

        Parameters
        ----------
        n : int
            Desired number of dice rows.
        """
        self.dice_data=[]
        self.add_dice_row(n)

    def get_n_dice_row(self)->int:
        """
        Get the current number of dice rows.

        Returns
        -------
        int
            The number of dice rows.
        """
        return len(self.dice_data)

    def get_dice_data(self)->list[tuple]:
        """
        Get a list of tuples containing a list of dice values followed by a piece of data about that row calculated by 'get_row_data(row)'

        Returns
        -------
        list of tuples
            each tuple contains a list of dice values followed by a value
        """
        return [([die.num for die in row],self.get_row_data(row)) for row in self.dice_data]

    def get_plot_data(self,show_real:bool=True)->tuple:
        """
        Generate data for plotting the distribution on a graph

        Parameters
        ----------
        show_real : bool
            If true, also return real x and real y values for plotting.
            If true, also return whether the real graph is 'line' or 'bar'

        Returns
        -------
        tuple
            contains x values, y values, real x values, real y values and real type
        """
        raise NotImplementedError

    def e_and_var(self, show_real:bool=True)->tuple:
        """
        Generate E(X) and Var(X)

        It generates the version from the simulation by calculating the mean and sample variance.
        It generates the real versions using the specific formulae.
        Parameters
        ----------
        show_real bool
            If true, also return real E(X) and real Var(X)

        Returns
        -------
        tuple
            contains E(X), Var(x), real E(X) and real Var(X)
        """
        raise NotImplementedError

class GeoDice(AbstractDicetribution):
    """
    Geometric dice distribution simulation

    Each dice row is rolled until a success value is reached.
    The row lengths are geometrically distributed.

    Attributes
    ----------
    _success_vals : list of int
        List of die numbers considered a "success" for stopping the roll.
    dice_data : list
        Inherited from AbstractDicetribution, stores all dice rows.
    parameters : dict
        Inherited from AbstractDicetribution, configuration parameters.
    """
    def __init__(self,parameters:dict=None)->None:
        """
        Initialise the Geometric Dice distribution.
        Parameters
        ----------
        parameters : dict
            Dictionary containing "num" (number of rows).
        """
        self._success_vals = [6]
        super().__init__(parameters)

    @property
    def success_vals(self)->list[int]:
        """
        Get the list of success values.

        Returns
        -------
        list of int
            Die numbers considered a "success".
        """
        return self._success_vals

    @success_vals.setter
    def success_vals(self, lst:list[int])->None:
        """
        Set the list of success values, and recreate the list of dice rows.
        Parameters
        ----------
        lst :list
            New list of die numbers considered a "success".
        """
        self._success_vals = lst
        self.set_n_dice_row(self.get_n_dice_row())

    def get_dice_row(self)->list[Die]:
        """
        Create a row of dice by rolling new dice until a success value is reached.
        Returns
        -------
        list of die
            A list of dice where the last one is a success value.
        """
        dice=[Die()]
        while dice[-1].num not in self.success_vals:
            dice.append(Die())
        return dice

    def get_plot_data(self, show_real:bool=True)->tuple:
        """
        Generate data for plotting the distribution on a graph

        In this case, the real distribution is a bar.

        Parameters
        ----------
        show_real : bool
            If true, also return real x and real y values for plotting.

        Returns
        -------
        tuple
            contains x values, y values, real x values, real y values and real type
        """
        x_vals=np.array([i for i in range(1,max(len(r) for r in self.dice_data)+1)])
        l_list=[len(r) for r in self.dice_data]
        y_vals=[l_list.count(i)/self.parameters["num"].value for i in x_vals]
        if not show_real:
            return x_vals, np.array(y_vals)
        p=len(self.success_vals)/6
        def pdf(x):
            return (1 - p) ** (x - 1) * p
        return x_vals, np.array(y_vals),x_vals,pdf(x_vals),"bar"

    def get_row_data(self,row:list[Die])->int:
        """
        Compute the row data as the length of the dice row.

        This is because the row lengths are what is distributed geometrically.

        Parameters
        ----------
        row:list of die
            The list of dice to calculate the length of

        Returns
        -------
        int
            Length of the dice row.
        """
        return len(row)

    def e_and_var(self, show_real:bool=True)->tuple:
        """
        Generate E(X) and Var(X)

        It generates the version from the simulation by calculating the mean and sample variance.
        It generates the real versions using the specific formulae.
        Parameters
        ----------
        show_real bool
            If true, also return real E(X) and real Var(X)

        Returns
        -------
        tuple
            contains E(X), Var(x), real E(X) and real Var(X)
        """
        e=mean([self.get_row_data(r) for r in self.dice_data])
        var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return e,var
        p = len(self.success_vals) / 6
        return e,var,1/p, (1-p)/(p**2)

class BinDice(AbstractDicetribution):
    """
    Binomial dice distribution simulation

    Each dice row is rolled n times.
    The number of success_vals in each row is binomially distributed.

    Attributes
    ----------
    success_vals : list of int
        List of die numbers considered a "success".
    dice_data : list
        Inherited from AbstractDicetribution, stores all dice rows.
    parameters : dict
        Inherited from AbstractDicetribution, contains configuration parameters.
    on_change : callable
        A function to refresh the controller when the parameters are changed.
    _cached_n : int
        A cached value of the 'n' parameter.
        Used to detect the changes
    """

    def __init__(self,parameters:dict[str:Parameter]=None,on_change:callable=None)->None:
        """
        Initialise the Binomial Dice distribution.
        Parameters
        ----------
        parameters : dict
            Dictionary containing "num" (number of rows), and "n" number of dice per row.
        on_change : callable
            A function to refresh the controller when the parameters are changed.
        """
        self.on_change = on_change
        self.success_vals = [6]
        self._cached_n = int(parameters["n"].value)
        super().__init__(parameters)

    # noinspection DuplicatedCode
    def _check_n_changed(self)->None:
        """
        Check whether n has changed when functions are called.

        This is always run at the start of a function.
        Refreshes the Dice before calculations are performed
        """
        current_n = int(self.parameters["n"].value)
        if self._cached_n != current_n:
            diff = current_n - self._cached_n
            self._cached_n = current_n
            for row in self.dice_data:
                if diff > 0:
                    for _ in range(diff):
                        row.append(Die())
                else:
                    for _ in range(-diff):
                        if len(row) > 0:
                            row.pop()
            self.on_change()

    def get_dice_row(self)->list[Die]:
        """
        Generate a row of dice of length `n`
        Returns
        -------
        list of Die
            list of dice, length `n`
        """
        self._check_n_changed()
        return [Die() for _ in range(int(self.parameters["n"].value))]

    def get_plot_data(self,show_real:bool=True)->tuple:
        """
        Generate data for plotting the distribution on a graph

        In this case, the real distribution is a bar.

        Parameters
        ----------
        show_real : bool
            If true, also return real x and real y values for plotting.

        Returns
        -------
        tuple
            contains x values, y values, real x values, real y values and real type
        """
        self._check_n_changed()
        x_vals=[i for i in range(int(self.parameters["n"].value)+1)]
        c_list=[count_multiple([die.num for die in r],self.success_vals) for r in self.dice_data]
        y_vals=[c_list.count(x) for x in x_vals]
        if not show_real:
            return x_vals, np.array(y_vals)/sum(y_vals)
        p=len(self.success_vals)/6
        def pdf(x):
            n=int(self.parameters["n"].value)
            return comb(n, x) * (p ** x) * ((1 - p) ** (n - x))
        return x_vals, np.array(y_vals)/sum(y_vals),x_vals,pdf(np.array(x_vals)),"bar"

    def get_row_data(self,row:list[Die])->int:
        """
        Calculate how many times a success value appears in a given row
        
        This is because the number of times that a value appears is binomially distributed.
        
        Parameters
        ----------
        row : list of Die
            List of dice to check for success values

        Returns
        -------
        int
            the number of times that a success value appears in the row
        """""
        self._check_n_changed()
        return count_multiple([die.num for die in row],self.success_vals)

    def e_and_var(self, show_real:bool=True)->tuple:
        """
        Generate E(X) and Var(X)

        It generates the version from the simulation by calculating the mean and sample variance.
        It generates the real versions using the specific formulae.

        Parameters
        ----------
        show_real bool
            If true, also return real E(X) and real Var(X)

        Returns
        -------
        tuple
            contains E(X), Var(x), real E(X) and real Var(X)
        """
        self._check_n_changed()
        e=mean([self.get_row_data(r) for r in self.dice_data])
        var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return e,var
        p = len(self.success_vals) / 6
        n=self.parameters["n"].value
        return e,var,n*p, (1-p)*n*p

class NormDice(AbstractDicetribution):
    """
    Normal dice distribution simulation

    Each dice row is rolled n times.
    The mean of each row is approximately normally distributed, by Central Limit Theorem.

    Attributes
    ----------
    dice_data : list
        Inherited from AbstractDicetribution, stores all dice rows.
    parameters : dict
        Inherited from AbstractDicetribution, contains configuration parameters.
    on_change : callable
        A function to refresh the controller when the parameters are changed.
    _cached_n : int
        A cached value of the 'n' parameter.
        Used to detect the changes
    """

    def __init__(self,parameters:dict[str:Parameter]=None,on_change:callable=None)->None:
        """
        Initialise the Normal Dice distribution.
        Parameters
        ----------
        parameters : dict
            Dictionary containing "num" (number of rows), and "n" number of dice per row.
        on_change : callable
            A function to refresh the controller when the parameters are changed.
        """
        self.on_change = on_change
        self._cached_n = int(parameters["n"].value)
        super().__init__(parameters)

    # noinspection DuplicatedCode
    def _check_n_changed(self)->None:
        """
        Check whether n has changed when functions are called.

        This is always run at the start of a function.
        Refreshes the Dice before calculations are performed
        """
        current_n = int(self.parameters["n"].value)
        if self._cached_n != current_n:
            diff = current_n - self._cached_n
            self._cached_n = current_n
            for row in self.dice_data:
                if diff > 0:
                    for _ in range(diff):
                        row.append(Die())
                else:
                    for _ in range(-diff):
                        if len(row) > 0:
                            row.pop()
            self.on_change()

    def get_dice_row(self)->list[Die]:
        """
        Generate a row of dice of length `n`
        Returns
        -------
        list of Die
            list of dice, length `n`
        """
        self._check_n_changed()
        return [Die() for _ in range(int(self.parameters["n"].value))]

    def get_plot_data(self,show_real:bool=True)->tuple:
        """
        Generate data for plotting the distribution on a graph

        The simulated distribution is plotted using a histogram.
        In this case, the real distribution is a line.

        Parameters
        ----------
        show_real : bool
            If true, also return real x and real y values for plotting.

        Returns
        -------
        tuple
            contains x values, y values, real x values, real y values and real type

        """
        self._check_n_changed()
        x_vals=np.linspace(1,6,21)
        a_list=[mean([dice.num for dice in row]) for row in self.dice_data]

        y_vals = [0] * len(x_vals)
        bin_width = x_vals[1] - x_vals[0]

        for value in a_list:
            if 1 <= value <= 6:
                index = int((value - 1) / bin_width)

                # Clamp right edge (value == 6)
                if index == len(x_vals):
                    index -= 1

                y_vals[index] += 1

        # y_vals=[]
        # for x in x_vals:
        #     upperbound=x+width
        #     y_vals.append(count_less_than_equal_to(a_list, upperbound) - sum(y_vals))
        if not show_real:
            return x_vals, y_vals

        mu=3.5
        sigma=np.sqrt(35/12) /np.sqrt(self.parameters["n"].value)
        width = (x_vals[1] - x_vals[0]) / 2

        def pdf(y):
            return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((y - mu) / sigma) ** 2)
        return x_vals, np.array(y_vals)/sum(y_vals),np.linspace(1,6,100),pdf(np.linspace(1,6,100))*width*2,"line"


    def get_row_data(self,row:list[Die])->float:
        """
        Calculate the mean of a given row

        This is because the mean is approximately normally distributed.

        Parameters
        ----------
        row : list of Die
            List of dice to calculate the mean.

        Returns
        -------
        float
            the mean value of the row
        """
        self._check_n_changed()
        return mean([die.num for die in row])

    def e_and_var(self, show_real:bool=True)->tuple:
        """
        Generate E(X) and Var(X)

        It generates the version from the simulation by calculating the mean and sample variance.
        It generates the real versions using the specific formulae.

        Parameters
        ----------
        show_real bool
            If true, also return real E(X) and real Var(X)

        Returns
        -------
        tuple
            contains E(X), Var(x), real E(X) and real Var(X)
        """

        self._check_n_changed()
        e=mean([self.get_row_data(r) for r in self.dice_data])
        var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return e,var
        return e,var,3.5, 35**2/144/self.parameters["n"].value

if __name__ == '__main__':
    PW=Piecewise([(1, 1), (2, 3), (3, 2)])
    print(PW.cdf(1),PW.cdf(2),PW.cdf(3))





