import numpy as np
import matplotlib.pyplot as plt

# noinspection DuplicatedCode
def piecewise_cubic_spline(points: list[tuple[float | int | np.float64, float | int | np.float64]]) -> list[np.ndarray]:
    """
    Compute the coefficients of piecewise cubic splines to connect given points.
    Parameters
    ----------
    points : list of tuple of float
        list of 2D points (x,y) to be interpolated.

    Returns
    -------
    list of np.ndarray
        A list of arrays representing cubic splines for each interval.
        Each array has the form [x1,x2,a,b,c,d].
        This represents the equation f(x) = a*x^3 + b*x^2 + c*x + d over the range [x1,x2]
    """
    points = sorted(points, key=lambda p: p[0])
    n = len(points) - 1

    matrix = np.zeros((4 * n, 4 * n))
    matb = np.zeros((4 * n, 1))

    ## f(X1) = y1, f(X2)=y2
    for i in range(n):
        matrix[2 * i][4 * i + 0] = points[i][0] ** 3
        matrix[2 * i][4 * i + 1] = points[i][0] ** 2
        matrix[2 * i][4 * i + 2] = points[i][0] ** 1
        matrix[2 * i][4 * i + 3] = points[i][0] ** 0
        matb[2 * i][0] = points[i][1]

        matrix[2 * i + 1][4 * i + 0] = points[i + 1][0] ** 3
        matrix[2 * i + 1][4 * i + 1] = points[i + 1][0] ** 2
        matrix[2 * i + 1][4 * i + 2] = points[i + 1][0] ** 1
        matrix[2 * i + 1][4 * i + 3] = points[i + 1][0] ** 0
        matb[2 * i + 1][0] = points[i + 1][1]

    ## f1'(x2)-f2'(x2)=0
    for i in range(n - 1):
        matrix[2 * n + i][4 * i + 0] = 3 * points[i + 1][0] ** 2
        matrix[2 * n + i][4 * i + 1] = 2 * points[i + 1][0] ** 1
        matrix[2 * n + i][4 * i + 2] = 1 * points[i + 1][0] ** 0

        matrix[2 * n + i][4 * i + 4] = -3 * points[i + 1][0] ** 2
        matrix[2 * n + i][4 * i + 5] = -2 * points[i + 1][0] ** 1
        matrix[2 * n + i][4 * i + 6] = -1 * points[i + 1][0] ** 0
    ## f1''(x2)-f2''(x2)=0
    for i in range(n - 1):
        matrix[2 * n + (n - 1) + i][4 * i + 0] = 6 * points[i + 1][0] ** 1
        matrix[2 * n + (n - 1) + i][4 * i + 1] = 2 * points[i + 1][0] ** 0

        matrix[2 * n + (n - 1) + i][4 * i + 4] = -6 * points[i + 1][0] ** 1
        matrix[2 * n + (n - 1) + i][4 * i + 5] = -2 * points[i + 1][0] ** 0
    # """
    ## f1''(x1)=0
    matrix[-2][0] = 6 * points[0][0]
    matrix[-2][1] = 2
    ## f(n-1))''(x(n-1))=0
    matrix[-1][-4] = 6 * points[-1][0]
    matrix[-1][-3] = 2

    coefficient_matrix = np.linalg.solve(matrix, matb)
    pieces = [np.array([points[i][0], points[i + 1][0], coefficient_matrix[4 * i][0], coefficient_matrix[4 * i + 1][0],
                        coefficient_matrix[4 * i + 2][0], coefficient_matrix[4 * i + 3][0]])
              for i in range(n)]
    return pieces


if __name__ == '__main__':
    pointls=[(0,0),(0.5,0),(1,2),(2,3),(3,4),(2.5,1)]
    piecels= piecewise_cubic_spline(pointls)

    plt.scatter(*zip(*pointls))
    for piecel in piecels:
        x1,x2,a,b,c,d=piecel
        x=np.linspace(x1, x2, 10)
        y=a*x**3 + b*x**2 +c*x +d
        plt.plot(x,y)
    plt.show()