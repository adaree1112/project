from scipy.stats import norm, binom, geom
from sympy import sympify, symbols

class DistributionModel:
    def __init__(self, distribution,args):
        self.args = args
        distdict={"G": geom, "B": binom, "N":norm}
        self.distribution = distdict[distribution]
        print(self.distribution)

    def probability(self,number):
        return self.distribution.pmf(number, *self.args) if hasattr(self.distribution, 'pmf') else self.distribution.pdf(number)

    def cumulative_probability(self,number):
        return self.distribution.cdf(number)

class InputtedPDFDistributionModel:
    def __init__(self, mini, pieces : dict):
        self.pieces = {k: v for k, v in sorted(pieces.items(), key=lambda item: item[1])}
        self.mini = mini
        print(self.pieces)

    # def probability(self,number):
    #     x = symbols("x")
    #
    #     if number < self.mini:
    #         return 0
    #     for piece in self.pieces:
    #         equation = sympify(piece[0])
    #         maxi = piece[1]
    #         if number < maxi:
    #             return equation.subs(x,number)

if __name__ == "__main__":
    # X = DistributionModel("G",[0.25])
    # print(X.probability(2))

    X = InputtedPDFDistributionModel(0,{"0.5x": 1, "1-0.5x": 2})
    print(X.probability(0))
    print(X.probability(1))
    print(X.probability(2))