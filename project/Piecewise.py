import random
import numpy as np
import math
from scipy.special import comb

from project.piecewisecubicsplines import piecewise_cubic_spline


def integrate_nbic(A, B,a,b,c,d,n): #defined for n>2
    return a * (B ** (n+1) - A ** (n+1)) / (n+1) + b * (B ** n - A ** n) / n + c * (B ** (n-1) - A ** (n-1)) / (n-1) + d * (B**(n-2) - A**(n-2))/(n-2)

class Piecewise:
    def __init__(self, points):
        self._points = points
        self.is_normalised = False
        self.pieces = []
        self.calculate_pieces()

    def get_points(self):
        return self._points

    def get_num_points(self):
        return len(self._points)

    def add_point(self):
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

    def remove_point(self):
        self.is_normalised = False
        if len(self._points) > 2:
            self._points.pop(random.randint(0, len(self._points) - 1))

    def calculate_pieces(self):
        sorted_points = sorted(self._points, key=lambda p: p[0])
        self.pieces = piecewise_cubic_spline(sorted_points)

    def update_point(self, old_x, old_y, new_x, new_y):
        for i, (x, y) in enumerate(self._points):
            if np.isclose(x,old_x) and np.isclose(y,old_y):
                self._points[i] = (new_x, new_y)
                self.is_normalised = False
                break

    def normalise(self):
        area = self.integrate_piecewise()
        k = 1 / area
        self._points = [(point[0], k * point[1]) for point in self._points]
        self.pieces = [np.concatenate((piece[:2], k * piece[2:])) for piece in self.pieces]
        self.is_normalised = True

    def integrate_piecewise(self,A=None, B=None):
        total = 0
        for p, piece in enumerate(self.pieces):
            x1, x2, a, b, c, d = piece
            if A and B:
                lower_bound = max(A, x1)
                upper_bound = min(B, x2)
            else:
                lower_bound = x1
                upper_bound = x2
            if lower_bound < upper_bound:
                total += integrate_nbic(lower_bound, upper_bound,a,b,c,d,3)
        return total

    def expectation(self,sq=False):
        total=0
        for piece in self.pieces:
            x1, x2, a, b, c, d = piece
            total+=integrate_nbic(x1,x2,a,b,c,d,4+sq)
        return total

    def variance(self):
        return self.expectation(sq=True) - self.expectation()**2




class AbstractStatisticalModel:
    def __init__(self, parameters, is_discrete, mini, maxi):
        self.parameters = parameters
        self.is_discrete = is_discrete
        self.mini = mini
        self.maxi = maxi

    def pdf(self,x):
        raise NotImplementedError

    def get_plot_data(self):
        if self.is_discrete:
            x_vals = np.array(range(self.mini, self.maxi))
            y_vals = self.pdf(x_vals)
            graphtype='bar'
        else:
            x_vals = np.linspace(self.mini, self.maxi, 100)
            y_vals = self.pdf(x_vals)
            graphtype='line'
        return x_vals, y_vals, graphtype

    def get_parameters(self):
        return self.parameters

    def cdf(self,x):
        total = 0.0

        if self.is_discrete:
            total=0.0
            for i in range (self.mini, x + 1):
                total+=self.pdf(i)
        else:
            n=1000
            h = float(x - self.mini) / n
            total += self.pdf(self.mini) / 2.0
            for i in range(1, n):
                total += self.pdf(self.mini + i * h)
            total += self.pdf(x) / 2.0
            total *= h
        return total

    def update_parameters(self, parameters):
        self.parameters = parameters

    def expectation(self):
        raise NotImplementedError

    def variance(self):
        raise NotImplementedError

class Normal(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        mu=parameters["mu"].value
        sigma=parameters["sigma"].value
        super().__init__(parameters,False,mu-5*sigma,mu+5*sigma)

    def pdf(self,x):
        mu=self.parameters["mu"].value
        sigma=self.parameters["sigma"].value
        return (1 / (sigma * np.sqrt(2 * math.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

    def expectation(self):
        mu=self.parameters["mu"].value
        return mu

    def variance(self):
        sigma=self.parameters["sigma"].value
        return sigma**2

class Binomial(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        n=parameters["n"].value
        super().__init__(parameters,True,0,n)

    def pdf(self,x):
        n=self.parameters["n"].value
        p=self.parameters["p"].value
        return comb(n, x) * (p ** x) * ((1 - p) ** (n - x))

    def expectation(self):
        n=self.parameters["n"].value
        p=self.parameters["p"].value
        return n*p

    def variance(self):
        n=self.parameters["n"].value
        p=self.parameters["p"].value
        return n*p *(1-p)

class Poisson(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        lam=parameters["lambda"].value
        super().__init__(parameters,True,0,int(lam+5*math.sqrt(lam)))

    def pdf(self,x):
        lam=self.parameters["lambda"].value
        return np.exp(-lam)*lam**x/math.factorial(x)

    def expectation(self):
        lam=self.parameters["lambda"].value
        return lam

    def variance(self):
        lam=self.parameters["lambda"].value
        return lam

class Geometric(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        p=parameters["p"].value
        super().__init__(parameters,True,1,int(1/p + 5*(1-p)**.5/p))

    def pdf(self,x):
        p=self.parameters["p"].value
        return (1-p)**(x-1)*p

    def expectation(self):
        p=self.parameters["p"].value
        return 1/p

    def variance(self):
        p=self.parameters["p"].value
        return (1-p)*p**-2

class Exponential(AbstractStatisticalModel):
    def __init__(self, parameters=None):
        lam=parameters["lambda"].value
        super().__init__(parameters,False,0,int(1/lam+5/lam))

    def pdf(self,x):
        lam=self.parameters["lambda"].value
        return lam*np.exp(-lam*x)

    def cdf(self,x):
        lam=self.parameters["lambda"].value
        return 1 - np.exp(-lam*x)

    def expectation(self):
        lam=self.parameters["lambda"].value
        return 1/lam

    def variance(self):
        lam=self.parameters["lambda"].value
        return lam**-2


class Parameter:
    def __init__(self, label, minimum, maximum, step, default):
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.value = default

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, value):
        self._value = value

    def get_spinbox_args(self):
        return {"from_":self.minimum, "to":self.maximum,"step":self.step},self.label







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




#TODO: CLASS PARAMETER
#TODO: TESTS
#TODO: DOUBLE CLICK TO ADD


if __name__ == '__main__':
    #import matplotlib.pyplot as plt
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