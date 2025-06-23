from scipy.stats import norm, binom, geom

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

# class InputtedPDFDistributionModel:
#     def __init__(self, pieces : dict):
#         self.pieces = sorted(pieces.values(), key=lambda x: x[1])
#         print(pieces)


if __name__ == "__main__":
    # X = DistributionModel("G",[0.25])
    # print(X.probability(2))

    # X = InputtedPDFDistributionModel({"(1-x)**2":1, "x**2":0.5})
