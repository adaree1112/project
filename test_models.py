import pytest
from models import Normal


class TestNormal:
    @pytest.fixture
    def standard_normal(self):
        class Parameter:
            def __init__(self, value):
                self.value = value

        return Normal(parameters={"mu": Parameter(0), "sigma": Parameter(1)})

    pdf_test_data = [(0.0, 0.3989422804), (1.0, 0.2419707245), (-1.0, 0.2419707245), (2.0, 0.0539909665),(-3.0, 0.0044318484), ]
    sym_cdf_test_data = [(-1.0, 1.0, 0.6826894921), (-2.0, 2.0, 0.9544997361), (-3.0, 3.0, 0.9973002039),(-0.5, 0.5, 0.3829249225), (-1.5, 1.5, 0.8663855974), ]
    cdf_test_data = [(-1.0, 0.1586552539), (0.0, 0.5), (1.0, 0.8413447461), (2.0, 0.9772498681), (-2.0, 0.0227501319)]
    asym_cdf_test_data = [(-1.0, 2.0, 0.9772498681 - 0.1586552539), (0.5, 2.5, 0.9937903347 - 0.6914624613),(1.0, 3.0, 0.9986501020 - 0.8413447461), (-3.0, 1.0, 0.8413447461 - 0.0013498980),(-0.5, 1.5, 0.9331927987 - 0.3085375387)]

    @pytest.mark.parametrize('x,p', pdf_test_data)
    def test_pdf(self, standard_normal, x, p):
        assert standard_normal.pdf(x) == pytest.approx(p, abs=1e-6)

    def test_mini(self, standard_normal):
        assert standard_normal.mini == -5

    def test_maxi(self, standard_normal):
        assert standard_normal.maxi == 5

    def test_expectation(self, standard_normal):
        assert standard_normal.expectation() == 0

    def test_variance(self, standard_normal):
        assert standard_normal.variance() == 1

    @pytest.mark.parametrize('a,b,p', sym_cdf_test_data)
    def test_xpexclusivein(self, a, b, p, standard_normal):
        assert standard_normal.xpexclusivein(p) == pytest.approx((a, b), abs=1e-3)

    @pytest.mark.parametrize('a,b,p', sym_cdf_test_data)
    def test_xpinclusivein(self, a, b, p, standard_normal):
        assert standard_normal.xpinclusivein(p) == pytest.approx((a, b), abs=1e-3)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_cdf(self, x, p, standard_normal):
        assert standard_normal.cdf(x) == pytest.approx(p, abs=1e-5)

    @pytest.mark.parametrize('x,_', pdf_test_data)
    def test_pxequals(self, x, standard_normal, _):
        assert standard_normal.pxequals(x) == 0

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_pxlessthan(self, x, p, standard_normal):
        assert standard_normal.pxlessthan(x) == pytest.approx(p, abs=1e-5)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_pxlessthanequalto(self, x, p, standard_normal):
        assert standard_normal.pxlessthanequalto(x) == pytest.approx(p, abs=1e-5)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_pxgreaterthan(self, x, p, standard_normal):
        assert standard_normal.pxgreaterthan(x) == pytest.approx(1-p, abs=1e-5)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_pxgreaterthanequalto(self, x, p, standard_normal):
        assert standard_normal.pxgreaterthanequalto(x) == pytest.approx(1-p, abs=1e-5)

    @pytest.mark.parametrize('a,b,p',asym_cdf_test_data+sym_cdf_test_data)
    def test_pxinclusivein(self,a,b,p,standard_normal):
        assert standard_normal.pxinclusivein(a,b) == pytest.approx(p, abs=1e-5)

    @pytest.mark.parametrize('a,b,p',asym_cdf_test_data+sym_cdf_test_data)
    def test_pxexclusivein(self,a,b,p,standard_normal):
        assert standard_normal.pxexclusivein(a,b) == pytest.approx(p, abs=1e-5)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_xplessthan(self,x,p,standard_normal):
        assert standard_normal.xplessthan(p) == pytest.approx(x, abs=1e-3)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_xplessthanequalto(self,x,p,standard_normal):
        assert standard_normal.xplessthanequalto(p) == pytest.approx(x, abs=1e-3)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_xpgreaterthan(self,x,p,standard_normal):
        assert standard_normal.xpgreaterthan(1-p) == pytest.approx(x, abs=1e-3)

    @pytest.mark.parametrize('x,p', cdf_test_data)
    def test_xpgreaterthanequalto(self,x,p,standard_normal):
        assert standard_normal.xpgreaterthanequalto(1-p) == pytest.approx(x, abs=1e-3)

