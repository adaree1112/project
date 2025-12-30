import random
import numpy as np
import math
from scipy.special import comb

from project.piecewisecubicsplines import piecewise_cubic_spline, piecewise_linear


def integrate_nbic(A, B, a, b, c, d, n):  # defined for n>2
    return a * (B ** (n + 1) - A ** (n + 1)) / (n + 1) + b * (B ** n - A ** n) / n + c * (
            B ** (n - 1) - A ** (n - 1)) / (n - 1) + d * (B ** (n - 2) - A ** (n - 2)) / (n - 2)


def binarysearchforx(targetp, minimum, maximum, func):
    middle = (minimum + maximum) / 2
    if np.isclose(func(middle), targetp, atol=1e-10):
        return middle
    if func(middle) < targetp:
        return binarysearchforx(targetp, middle, maximum, func)
    elif func(middle) > targetp:
        return binarysearchforx(targetp, minimum, middle, func)
    return None

def mean(l):
    if len(l)==0:
        return -1
    return sum(l)/len(l)

def sample_var(l):
    n=len(l)
    if n==1:
        return -1
    return (sum(x**2 for x in l) / (n - 1)) - (n / (n - 1)) * mean(l)**2

def count_multiple(l, value_list):
    return sum(l.count(value) for value in value_list)

def count_less_than(l,x):
    return sum([1 for i in l if i<=x])

class Piecewise:
    def __init__(self, points):
        self.is_discrete = False
        self._points = points
        self.is_normalised = False
        self.pieces = []
        self.calculate_pieces()

    @property
    def mini(self):
        x, y = zip(*self._points)
        return min(x)

    @property
    def maxi(self):
        x, y = zip(*self._points)
        return max(x)

    def get_points(self):
        return self._points

    def get_num_points(self):
        return len(self._points)

    def add_point(self, point=None):
        if point is None:
            self.is_normalised = False
            if not self._points:
                self._points.append([(0, 0), (1, 1)])
            elif len(self._points) < 2:
                if self._points[0] != (1, 1):
                    self._points.append([(1, 1)])
                else:
                    self._points.append([(0, 0)])
            else:
                currx, curry = zip(*self._points)
                new_x = random.uniform(min(currx), max(currx))
                new_y = random.uniform(0, max(curry))
                self._points.append((new_x, new_y))
        else:
            self._points.append(point)

    def remove_point(self):
        self.is_normalised = False
        if len(self._points) > 2:
            self._points.pop(random.randint(0, len(self._points) - 1))

    def calculate_pieces(self, linear=False):
        sorted_points = sorted(self._points, key=lambda p: p[0])
        if not linear:
            self.pieces = piecewise_cubic_spline(sorted_points)
        else:
            self.pieces = piecewise_linear(sorted_points)

    def update_point(self, old_x, old_y, new_x, new_y):
        for i, (x, y) in enumerate(self._points):
            if np.isclose(x, old_x) and np.isclose(y, old_y):
                self._points[i] = (new_x, new_y)
                self.is_normalised = False
                break

    def normalise(self):
        area = self.integrate_piecewise()
        k = 1 / area
        self._points = [(point[0], k * point[1]) for point in self._points]
        self.pieces = [np.concatenate((piece[:2], k * piece[2:])) for piece in self.pieces]
        self.is_normalised = True

    def integrate_piecewise(self, A=None, B=None):
        total = 0
        for p, piece in enumerate(self.pieces):
            x1, x2, a, b, c, d = piece

            lower_bound = x1
            upper_bound = x2
            if A is not None:
                lower_bound = max(A, x1)
            if B is not None:
                upper_bound = min(B, x2)

            if lower_bound < upper_bound:
                total += integrate_nbic(lower_bound, upper_bound, a, b, c, d, 3)
        return total

    def expectation(self, sq=False):
        total = 0
        for piece in self.pieces:
            x1, x2, a, b, c, d = piece
            total += integrate_nbic(x1, x2, a, b, c, d, 4 + sq)
        return total

    def variance(self):
        return self.expectation(sq=True) - self.expectation() ** 2

    def cdf(self, x_vals):
        if isinstance(x_vals, np.ndarray):
            return [self.pxlessthan(x) for x in x_vals]
        else:
            return self.pxlessthan(x_vals)

    def pxlessthan(self, x):
        return self.integrate_piecewise(B=x)

    def pxequals(self, x):
        return None

    def pxlessthanequalto(self, x):
        return self.pxlessthan(x)

    def pxgreaterthan(self, x):
        return 1 - self.pxlessthan(x)

    def pxgreaterthanequalto(self, x):
        return self.pxgreaterthan(x)

    def pxinclusivein(self, a, b):
        return self.pxlessthan(b) - self.pxlessthan(a)

    def pxexclusivein(self, a, b):
        return self.pxinclusivein(a, b)

    # FIND p from x
    def xplessthan(self, p):
        xs = [pt[0] for pt in self._points]
        return binarysearchforx(p, min(xs), max(xs), self.pxlessthan)

    def xplessthanequalto(self, p):
        return self.xplessthan(p)

    def xpgreaterthan(self, p):
        return self.xplessthan(1 - p)

    def xpgreaterthanequalto(self, p):
        return self.xpgreaterthan(p)

    def xpinclusivein(self, p):
        raise NotImplementedError

    def xpexclusivein(self, p):
        raise NotImplementedError


class AbstractStatisticalModel:
    def __init__(self, parameters, is_discrete, ):
        self.parameters = parameters
        self.is_discrete = is_discrete
        self.x = 0

    @property
    def mini(self):
        raise NotImplementedError

    @property
    def maxi(self):
        raise NotImplementedError

    def pdf(self, x):
        raise NotImplementedError

    def get_plot_data(self):
        if self.is_discrete:
            x_vals = np.array(range(self.mini, self.maxi))
            y_vals = self.pdf(x_vals)
            graphtype = 'bar'
        else:
            x_vals = np.linspace(self.mini, self.maxi, 100)
            y_vals = self.pdf(x_vals)
            graphtype = 'line'
        return x_vals, y_vals, graphtype, self.pxlessthanequalto

    def get_parameters(self):
        return self.parameters

    def cdf(self, x):

        if isinstance(x, np.ndarray):
            return [self.cdf(c) for c in x]
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
    def pxequals(self, x):
        if self.is_discrete:
            if self.mini <= x <= self.maxi:
                return self.pdf(x)
        return 0

    def pxlessthan(self, x):
        if self.mini <= x:
            if self.is_discrete:
                return self.cdf(min(x - 1, self.maxi))
            else:
                return self.cdf(min(x, self.maxi))
        return 0

    def pxlessthanequalto(self, x):
        if self.is_discrete:
            return self.pxlessthan(x + 1)
        else:
            return self.pxlessthan(x)

    def pxgreaterthan(self, x):
        return 1 - self.pxlessthanequalto(x)

    def pxgreaterthanequalto(self, x):
        return 1 - self.pxlessthan(x)

    def pxinclusivein(self, a, b):
        if self.is_discrete:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a - 1)
        else:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a)

    def pxexclusivein(self, a, b):
        return self.pxlessthan(b) - self.pxlessthan(a)

    # FIND p from x
    def xplessthan(self, p):
        if self.is_discrete:
            prevx = None
            for x in range(self.mini, self.maxi + 1):
                if self.pxlessthan(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p, self.mini, self.maxi, self.pxlessthan)

    def xplessthanequalto(self, p):
        if self.is_discrete:
            prevx = None
            for x in range(self.mini, self.maxi + 1):
                if self.pxlessthanequalto(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p, self.mini, self.maxi, self.pxlessthan)

    def xpgreaterthan(self, p):
        if self.is_discrete:
            prevx = None
            for x in range(self.maxi, self.mini - 1, -1):
                if self.pxgreaterthan(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p, self.maxi, self.mini, self.pxgreaterthan)

    def xpgreaterthanequalto(self, p):
        if self.is_discrete:
            prevx = None
            for x in range(self.maxi, self.mini - 1, -1):
                if self.pxgreaterthanequalto(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p, self.maxi, self.mini, self.pxgreaterthan)

    def xpinclusivein(self, p):
        raise NotImplementedError

    def xpexclusivein(self, p):
        raise NotImplementedError

    def expectation(self):
        raise NotImplementedError

    def variance(self):
        raise NotImplementedError


class Normal(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        super().__init__(parameters, False)

    def pdf(self, x):
        mu = self.parameters["mu"].value
        sigma = self.parameters["sigma"].value
        return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

    @property
    def mini(self):
        return self.expectation() - 5 * self.variance() ** .5

    @property
    def maxi(self):
        return self.expectation() + 5 * self.variance() ** .5

    def expectation(self):
        mu = self.parameters["mu"].value
        return mu

    def variance(self):
        sigma = self.parameters["sigma"].value
        return sigma ** 2

    def xpexclusivein(self, p):
        mu = self.parameters["mu"].value

        def xbetweenmuandx(x):
            return self.cdf(x) - self.pxlessthan(mu)

        distance_from_mean = binarysearchforx(p / 2, self.mini, self.maxi, xbetweenmuandx) - mu
        return mu - distance_from_mean, mu + distance_from_mean

    def xpinclusivein(self, p):
        return self.xpexclusivein(p)


class Binomial(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        super().__init__(parameters, True)

    @property
    def mini(self):
        return 0

    @property
    def maxi(self):
        return int(self.parameters["n"].value)

    def pdf(self, x):
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return comb(n, x) * (p ** x) * ((1 - p) ** (n - x))

    def expectation(self):
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return n * p

    def variance(self):
        n = self.parameters["n"].value
        p = self.parameters["p"].value
        return n * p * (1 - p)


class Poisson(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        super().__init__(parameters, True)

    @property
    def mini(self):
        return 0

    @property
    def maxi(self):
        return int(self.expectation() + 5 * self.variance() ** .5)

    def pdf(self, x):
        if isinstance(x, np.ndarray):
            return [self.pdf(c) for c in x]
        lam = self.parameters["lambda"].value
        return np.exp(-lam) * lam ** x / math.factorial(x)

    def expectation(self):
        lam = self.parameters["lambda"].value
        return lam

    def variance(self):
        lam = self.parameters["lambda"].value
        return lam


class Geometric(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        super().__init__(parameters, True)

    @property
    def mini(self):
        return 0

    @property
    def maxi(self):
        return int(self.expectation() + 5 * self.variance() ** .5)

    def pdf(self, x):
        p = self.parameters["p"].value
        return (1 - p) ** (x - 1) * p

    def expectation(self):
        p = self.parameters["p"].value
        return 1 / p

    def variance(self):
        p = self.parameters["p"].value
        return (1 - p) * p ** -2


class Exponential(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        super().__init__(parameters, False)

    @property
    def mini(self):
        return 0

    @property
    def maxi(self):
        return self.expectation() + 5 * self.variance() ** .5

    def pdf(self, x):
        lam = self.parameters["lambda"].value
        return lam * np.exp(-lam * x)

    def cdf(self, x):
        lam = self.parameters["lambda"].value
        return 1 - np.exp(-lam * x)

    def expectation(self):
        lam = self.parameters["lambda"].value
        return 1 / lam

    def variance(self):
        lam = self.parameters["lambda"].value
        return lam ** -2


class Parameter:
    def __init__(self, label, minimum, maximum, step, default):
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.default = default
        self._value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            v = float(value)
            if self.minimum <= v <= self.maximum:
                self._value = v
        except ValueError:
            pass

    def get_label(self):
        return self.label + " = "

    def validate(self, value, ):
        try:
            v = float(value)
            return self.minimum <= v <= self.maximum
        except ValueError:
            return False

    def get_spinbox_args(self):
        return {"from_": self.minimum, "to": self.maximum, "increment": self.step, "width": 5}


class Die:
    def __init__(self):
        self.num = 0
        self.roll()

    def roll(self):
        self.num = random.randint(1, 6)
        return self.num


class AbstractDicetribution:
    def __init__(self,parameters=None,on_change=None):
        self.dice_data = []
        self.parameters = parameters
        self.set_n_dice_row(self.parameters["num"].value)

    def get_dice_row(self):
        raise NotImplementedError

    def get_row_data(self,row):
        raise NotImplementedError

    def add_dice_row(self, n=1):
        for i in range(int(n)):
            self.dice_data.append(self.get_dice_row())
        if n<0:
            self.remove_dice_row(n=-n)

    def remove_dice_row(self, n=1):
        for i in range(int(n)):
            self.dice_data.pop()

    def set_n_dice_row(self, n):
        self.dice_data=[]
        self.add_dice_row(n)

    def get_n_dice_row(self):
        return len(self.dice_data)

    def get_dice_data(self):
        return [([die.num for die in row],self.get_row_data(row)) for row in self.dice_data]

    def get_plot_data(self,show_real):
        raise NotImplementedError

    def EandVar(self,showreal):
        raise NotImplementedError

class GeoDice(AbstractDicetribution):
    def __init__(self,parameters=None):
        self._success_vals = [6]
        super().__init__(parameters)

    @property
    def success_vals(self):
        return self._success_vals

    @success_vals.setter
    def success_vals(self, lst):
        self._success_vals = lst
        self.set_n_dice_row(self.get_n_dice_row())

    def get_dice_row(self):
        dice=[Die()]
        while dice[-1].num not in self.success_vals:
            dice.append(Die())
        return dice

    def get_plot_data(self, show_real):
        x_vals=np.array([i for i in range(1,max(len(r) for r in self.dice_data)+1)])
        l_list=[len(r) for r in self.dice_data]
        y_vals=[l_list.count(i)/self.parameters["num"].value for i in x_vals]
        if not show_real:
            return x_vals, y_vals
        p=len(self.success_vals)/6
        def pdf(x,p):
            return (1 - p) ** (x - 1) * p
        return x_vals, y_vals,x_vals,pdf(x_vals,p),"bar"

    def get_row_data(self,row):
        return len(row)

    def EandVar(self,show_real):
        x_vals,y_vals=self.get_plot_data(False)
        E=mean([self.get_row_data(r) for r in self.dice_data])
        Var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return E,Var
        p = len(self.success_vals) / 6
        return E,Var,1/p, (1-p)/(p**2)

class BinDice(AbstractDicetribution):
    def __init__(self,parameters=None,on_change=None):
        self.on_change = on_change
        self.success_vals = [6]
        self._cached_n = int(parameters["n"].value)
        super().__init__(parameters)

    def _check_n_changed(self):
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

    def get_dice_row(self):
        self._check_n_changed()
        return [Die() for _ in range(int(self.parameters["n"].value))]

    def get_plot_data(self,show_real):
        self._check_n_changed()
        x_vals=[i for i in range(int(self.parameters["n"].value))]
        c_list=[count_multiple([die.num for die in r],self.success_vals) for r in self.dice_data]
        y_vals=[c_list.count(x) for x in x_vals]
        if not show_real:
            return x_vals, y_vals
        p=len(self.success_vals)/6
        def pdf(x,p):
            n=int(self.parameters["n"].value)
            return comb(n, x) * (p ** x) * ((1 - p) ** (n - x))
        return x_vals, y_vals,x_vals,pdf(x_vals,p),"bar"

    def get_row_data(self,row):
        self._check_n_changed()
        return count_multiple([die.num for die in row],self.success_vals)

    def EandVar(self,show_real):
        self._check_n_changed()
        x_vals,y_vals=self.get_plot_data(False)
        E=mean([self.get_row_data(r) for r in self.dice_data])
        Var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return E,Var
        p = len(self.success_vals) / 6
        n=self.parameters["n"].value
        return E,Var,n*p, (1-p)*n*p

class NormDice(AbstractDicetribution):
    def __init__(self,parameters=None,on_change=None):
        self.on_change = on_change
        self.success_vals = [6]
        self._cached_n = int(parameters["n"].value)
        super().__init__(parameters)

    def _check_n_changed(self):
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

    def get_dice_row(self):
        self._check_n_changed()
        return [Die() for _ in range(int(self.parameters["n"].value))]

    def get_plot_data(self,show_real):
        self._check_n_changed()
        x_vals=np.linspace(1,6,41)
        a_list=[mean([dice.num for dice in row]) for row in self.dice_data]
        y_vals=[]
        width = (x_vals[1] - x_vals[0]) / 2
        for x in x_vals:
            upperbound=x+width
            y_vals.append(count_less_than(a_list,upperbound) - sum(y_vals))
        if not show_real:
            return x_vals, y_vals

        mu=3.5
        sigma=np.sqrt(35/12) /np.sqrt(self.parameters["n"].value)

        def pdf(x):
            return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
        return x_vals, np.array(y_vals)/sum(y_vals),x_vals,pdf(x_vals)*width*2,"line"


    def get_row_data(self,row):
        self._check_n_changed()
        return mean([die.num for die in row])

    def EandVar(self,show_real):
        self._check_n_changed()
        x_vals,y_vals=self.get_plot_data(False)
        E=mean([self.get_row_data(r) for r in self.dice_data])
        Var=sample_var([self.get_row_data(r) for r in self.dice_data])
        if not show_real:
            return E,Var
        return E,Var,3.5, 35**2/144/self.parameters["n"].value







