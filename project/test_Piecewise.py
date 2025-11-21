import pytest
from project.Piecewise import Normal,Parameter

class TestNormal:

    @pytest.fixture()
    def normal(self):
        params = {"mu": Parameter("μ", -999, 999, 0.1, 0),
                  "sigma": Parameter("σ", 0.1, 999, 0.1, 1)}
        return Normal(params)

    #n.b. AI generated the test data
    pdf_data = [
        (-4.0, 0.00013383022576488537),
        (-3.75, 0.00036333958049456853),
        (-3.5, 0.0008726826950457602),
        (-3.25, 0.0019930310032383763),
        (-3.0, 0.0044318484119380075),
        (-2.75, 0.009145904254152461),
        (-2.5, 0.01752830049356854),
        (-2.25, 0.03173965101680194),
        (-2.0, 0.05399096651318806),
        (-1.75, 0.08627731882651136),
        (-1.5, 0.12951759566589174),
        (-1.25, 0.18264908538939952),
        (-1.0, 0.24197072451914337),
        (-0.75, 0.30113743215480444),
        (-0.5, 0.3520653267642995),
        (-0.25, 0.38666811680284924),
        (0.0, 0.3989422804014327),
        (0.25, 0.38666811680284924),
        (0.5, 0.3520653267642995),
        (0.75, 0.30113743215480444),
        (1.0, 0.24197072451914337),
        (1.25, 0.18264908538939952),
        (1.5, 0.12951759566589174),
        (1.75, 0.08627731882651136),
        (2.0, 0.05399096651318806),
        (2.25, 0.03173965101680194),
        (2.5, 0.01752830049356854),
        (2.75, 0.009145904254152461),
        (3.0, 0.0044318484119380075),
        (3.25, 0.0019930310032383763),
        (3.5, 0.0008726826950457602),
        (3.75, 0.00036333958049456853),
        (4.0, 0.00013383022576488537),
    ]

    @pytest.mark.parametrize("x,p",pdf_data)
    def test_pdf(self,normal,x,p):
        assert normal.pdf(x)==pytest.approx(p,4)

    def test_mini(self,normal):
        assert False

    def test_maxi(self,normal):
        assert False

    def test_expectation(self,normal):
        assert False

    def test_variance(self,normal):
        assert False

    def test_xpexclusivein(self,normal):
        assert False

    def test_xpinclusivein(self,normal):
        assert False
