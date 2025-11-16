import random
import numpy as np
import math
from scipy.special import comb

from project.piecewisecubicsplines import piecewise_cubic_spline


def integrate_nbic(A, B, a, b, c, d, n):  # defined for n>2
    return a * (B ** (n + 1) - A ** (n + 1)) / (n + 1) + b * (B ** n - A ** n) / n + c * (
                B ** (n - 1) - A ** (n - 1)) / (n - 1) + d * (B ** (n - 2) - A ** (n - 2)) / (n - 2)


def binarysearchforx(targetp, minimum, maximum, func):
    middle = (minimum + maximum) / 2
    if np.isclose(func(middle), targetp):
        return middle
    if func(middle) < targetp:
        return binarysearchforx(targetp, middle, maximum, func)
    elif func(middle) > targetp:
        return binarysearchforx(targetp, minimum, middle, func)
    return None

class Piecewise:
    def __init__(self, points):
        self.is_discrete = False
        self._points = points
        self.is_normalised = False
        self.pieces = []
        self.calculate_pieces()

    @property
    def mini(self):
        x,y=zip(*self._points)
        return min(x)

    @property
    def maxi(self):
        x,y=zip(*self._points)
        return max(x)

    def get_points(self):
        return self._points

    def get_num_points(self):
        return len(self._points)

    def add_point(self,point=None):
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

    def calculate_pieces(self):
        sorted_points = sorted(self._points, key=lambda p: p[0])
        self.pieces = piecewise_cubic_spline(sorted_points)

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
            if A:
                lower_bound = max(A, x1)
            if B:
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

    def pxlessthan(self,x):
        return self.integrate_piecewise(B=x)

    def pxlessthanequalto(self,x):
        return self.pxlessthan(x)

    def pxgreaterthan(self,x):
        return 1-self.pxlessthan(x)

    def pxgreaterthanequalto(self,x):
        return self.pxgreaterthan(x)

    def pxinclusivein(self, a, b):
        return self.pxlessthan(b)-self.pxlessthan(a)

    def pxexclusivein(self,a,b):
        return self.pxinclusivein(a,b)

    #FIND p from x
    def xplessthan(self,p):
        xs = [pt[0] for pt in self._points]
        return binarysearchforx(p,min(xs),max(xs),self.pxlessthan)

    def xplessthanequalto(self,p):
        return self.xplessthan(p)

    def xpgreaterthan(self,p):
        return self.xplessthan(1-p)

    def xpgreaterthanequalto(self,p):
        return self.xpgreaterthan(p)

    def xpinclusivein(self,p):
        raise NotImplementedError

    def xpexclusivein(self,p):
        raise NotImplementedError




class AbstractStatisticalModel:
    def __init__(self, parameters, is_discrete,):
        self.parameters = parameters
        self.is_discrete = is_discrete

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
            cdf_vals=None
        else:
            x_vals = np.linspace(self.mini, self.maxi, 100)
            y_vals = self.pdf(x_vals)
            graphtype = 'line'
            cdf_vals=self.cdf(x_vals)
        return x_vals, y_vals, graphtype, cdf_vals

    def get_parameters(self):
        return self.parameters

    def cdf(self, x):

        if isinstance(x,np.ndarray):
            return [self.cdf(c) for c in x]
        total = 0.0

        if self.is_discrete:
            total = 0.0
            for i in range(self.mini, x + 1):
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
    def pxequals(self,x):
        if self.is_discrete:
            if self.mini <= x <= self.maxi:
                return self.pdf(x)
        return 0

    def pxlessthan(self,x):
        if self.mini <= x :
            if self.is_discrete:
                return self.cdf(min(x-1,self.maxi))
            else:
                return self.cdf(min(x,self.maxi))
        return 0

    def pxlessthanequalto(self,x):
        if self.is_discrete:
            return self.pxlessthan(x+1)
        else:
            return self.pxlessthan(x)

    def pxgreaterthan(self,x):
        return 1-self.pxlessthanequalto(x)

    def pxgreaterthanequalto(self,x):
        return 1-self.pxlessthan(x)

    def pxinclusivein(self, a, b):
        if self.is_discrete:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a - 1)
        else:
            return self.pxlessthanequalto(b) - self.pxlessthanequalto(a)

    def pxexclusivein(self,a,b):
        return self.pxlessthan(b)-self.pxlessthan(a)
    #FIND p from x
    def xplessthan(self,p):
        if self.is_discrete:
            prevx = None
            for x in range(self.mini, self.maxi+1):
                if self.pxlessthan(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p,self.mini,self.maxi,self.pxlessthan)

    def xplessthanequalto(self,p):
        if self.is_discrete:
            prevx = None
            for x in range(self.mini, self.maxi+1):
                if self.pxlessthanequalto(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p,self.mini,self.maxi,self.pxlessthan)

    def xpgreaterthan(self,p):
        if self.is_discrete:
            prevx = None
            for x in range(self.maxi, self.mini-1,-1):
                if self.pxgreaterthan(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p,self.maxi,self.mini,self.pxgreaterthan)

    def xpgreaterthanequalto(self,p):
        if self.is_discrete:
            prevx = None
            for x in range(self.maxi, self.mini-1,-1):
                if self.pxgreaterthanequalto(x) <= p:
                    prevx = x
                else:
                    break
            return prevx
        else:
            return binarysearchforx(p,self.maxi,self.mini,self.pxgreaterthan)

    def xpinclusivein(self,p):
        raise NotImplementedError

    def xpexclusivein(self,p):
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
        return (1 / (sigma * np.sqrt(2 * math.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

    @property
    def mini(self):
        return self.expectation()-5*self.variance()**.5

    @property
    def maxi(self):
        return self.expectation()+5*self.variance()**.5

    def expectation(self):
        mu = self.parameters["mu"].value
        return mu

    def variance(self):
        sigma = self.parameters["sigma"].value
        return sigma ** 2

    def xpexclusivein(self,p):
        mu=self.parameters["mu"].value
        def xbetweenmuandx(x):
            return self.cdf(x)-self.pxlessthan(mu)
        distance_from_mean=binarysearchforx(p/2,self.mini,self.maxi,xbetweenmuandx)
        return mu - distance_from_mean, mu + distance_from_mean

    def xpinclusivein(self,p):
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
        return int(self.expectation()+5*self.variance()**.5)

    def pdf(self, x):
        if isinstance(x,np.ndarray):
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
        return int(self.expectation()+5*self.variance()**.5)

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
        return self.expectation()+5*self.variance()**.5

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
        return self.label+" = "

    def validate(self, value,):
        print("hello")
        try:
            v = float(value)
            return self.minimum <= v <= self.maximum
        except ValueError:
            return False

    def get_spinbox_args(self):
        return {"from_": self.minimum, "to": self.maximum, "increment": self.step,"width":5}


"""@startuml
class "Piecewise"{
-points: List
+pieces: List
+get_points()
+get_num_points()
+add_point()
+remove_point()
+calculate_pieces()
+update_point()
+normalise()
+integrate_piecewise()
+expectation()
+variance()
}

abstract "AbstractStatisticalModel"{
+parameters: List
+is_discrete: Bool
+mini: Float
+maxi: Float
+pdf() - not impletented
+get_plot_data()
+get_parameters()
+cdf()
+update_parameters()
+expectation() - not implemented
+variance() - not implemented
}

class Normal{
+pdf()
+expectation()
+variance()
}
AbstractStatisticalModel<|--Normal

class Binomial{
+pdf()
+expectation()
+variance()
}
AbstractStatisticalModel<|--Binomial

class Poisson{
+pdf()
+expectation()
+variance()
}
AbstractStatisticalModel<|--Poisson

class Geometric{
+pdf()
+expectation()
+variance()
}
AbstractStatisticalModel<|--Geometric

class Exponential{
+pdf()
+expectation()
+variance()
+cdf()
}
AbstractStatisticalModel<|--Exponential

class Parameters{
    - label
    - minimum
    - maximum
    - step
    + value <<property>>
    + value() <<setter>>
    + get_spinbox_args()
}

Binomial o--	 Parameters
Normal o--	 Parameters
Geometric o--	 Parameters
Poisson o--	 Parameters
Exponential o--	 Parameters
@enduml"""

# TODO: CLASS PARAMETER
# TODO: TESTS
# TODO: DOUBLE CLICK TO ADD



if __name__ == '__main__':

    # import matplotlib.pyplot as plt
    pmu=Parameter("mu",-999,999,1,0)
    psigma=Parameter("sigma",-999,999,1,1)

    norm=Normal({"mu":pmu,"sigma":psigma})
    print(norm.xpinclusivein(0.4))

    """
    x,y,t=Binomial({"n":10,"p":0.25}).get_plot_data()
    if t == 'line':
        plt.plot(x,y)
    elif t == 'bar':
        print(x,y)
        plt.bar(x,y)
    plt.show()
    

    model=Normal({"sigma":10,"mu":0.25})#
    print(model.cdf(3))
    """
