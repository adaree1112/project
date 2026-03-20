def expectation(self) -> float:
    """
    Mean (expected value) of the geometric distribution.

    Returns
    -------
    float
    """
    p = self.parameters["p"].value
    try:
        output=1/p
    except ZeroDivisionError:
        output=-1
        print("ZeroDivisionError")
    return output


def variance(self) -> float:
    """
    Variance of the geometric distribution.

    Returns
    -------
    float
    """
    p = self.parameters["p"].value
    try:
        output=(1 - p) * p ** -2
    except ZeroDivisionError:
        output=-1
        print("ZeroDivisionError")
    return output