import numpy as np

def merge_sort(to_sort, key=lambda x: x):
    if len(to_sort) == 1:
        return to_sort

    middle = len(to_sort) // 2
    left_half = to_sort[:middle]
    right_half = to_sort[middle:]

    left_half = merge_sort(left_half, key=key)
    right_half = merge_sort(right_half, key=key)

    return merge(left_half, right_half, key)


def merge(left, right, key):
    result = []
    l = 0
    r = 0

    while l < len(left) and r < len(right):
        if key(left[l]) < key(right[r]):
            result.append(left[l])
            l += 1
        else:  # priority to left if equal
            result.append(right[r])
            r += 1

    result.extend(left[l:])
    result.extend(right[r:])

    return result


def piecewise_cubic_spline(points:list[tuple[float|int|np.float64,float|int|np.float64]])->list[np.ndarray]:
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
    points = merge_sort(points, key=lambda p: p[0])
    n=len(points)-1

    matrix=np.zeros((4*n,4*n))
    matb=np.zeros((4*n,1))

    ## f(X1) = y1, f(X2)=y2
    for i in range(n):

        matrix[2*i,4*i+0] = points[i][0]**3
        matrix[2*i,4*i+1] = points[i][0]**2
        matrix[2*i,4*i+2] = points[i][0]**1
        matrix[2*i,4*i+3] = points[i][0]**0
        matb[2*i,0]=points[i][1]

        matrix[2*i+1,4*i+0] = points[i+1][0] ** 3
        matrix[2*i+1,4*i+1] = points[i+1][0] ** 2
        matrix[2*i+1,4*i+2] = points[i+1][0] ** 1
        matrix[2*i+1,4*i+3] = points[i+1][0] ** 0
        matb[2*i+1,0] = points[i+1][1]

    ## f1'(x2)-f2'(x2)=0
    for i in range(n-1):
        matrix[2*n+i,4*i+0] = 3*points[i+1][0]**2
        matrix[2*n+i,4*i+1] = 2*points[i+1][0]**1
        matrix[2*n+i,4*i+2] = 1*points[i+1][0]**0

        matrix[2*n+i,4*i+4] = -3*points[i+1][0]**2
        matrix[2*n+i,4*i+5] = -2*points[i+1][0]**1
        matrix[2*n+i,4*i+6] = -1*points[i+1][0]**0
    ## f1''(x2)-f2''(x2)=0
    for i in range(n-1):
        matrix[2*n+(n-1)+i,4*i+0] = 6*points[i+1][0]**1
        matrix[2*n+(n-1)+i,4*i+1] = 2*points[i+1][0]**0

        matrix[2*n+(n-1)+i,4*i+4] = -6*points[i+1][0]**1
        matrix[2*n+(n-1)+i,4*i+5] = -2*points[i+1][0]**0
    #"""
    ## f1''(x1)=0
    matrix[-2,0]=6*points[0][0]
    matrix[-2,1]=2
    ## f(n-1))''(x(n-1))=0
    matrix[-1,-4]=6*points[-1][0]
    matrix[-1,-3]=2

    coefficient_matrix=np.linalg.solve(matrix,matb)
    pieces=[np.array([points[i][0],points[i+1][0],coefficient_matrix[4*i][0],coefficient_matrix[4*i+1][0],coefficient_matrix[4*i+2][0],coefficient_matrix[4*i+3][0]])
            for i in range(n)]
    pieces=deal_with_negatives(pieces)
    return pieces

def piecewise_linear(points: list[tuple[float, float]]) -> list[np.ndarray]:
    """
    Computes the coefficients of piecewise linear splines to connect given points.

    Parameters
    ----------
    points : list of tuple of float
        list of 2D points (x,y) to be interpolated.

    Returns
    -------
    list of np.ndarray
        A list of arrays representing linear interpolation for each interval.
        Each array has the form [x1,x2,a,b,c,d].
        This represents the equation f(x) = a*x^3 + b*x^2 + c*x + d over the range [x1,x2]
        The coefficient of the high order terms, a and b, are 0

    """
    points = merge_sort(points, key=lambda p: p[0])

    output = []
    for point, next_point in zip(points, points[1:]):
        if point == next_point:
            continue
        x1, y1 = point
        x2, y2 = next_point
        c = (y2 - y1) / (x2 - x1)
        d = y1 - c * x1
        output.append(np.array([x1, x2, 0, 0, c,d]))
    return output

def deal_with_negatives(pieces:list[np.ndarray]) -> list[np.ndarray]:
    """
    Deals with any negative values in the computed splines.

    It checks for roots in each section and if there are roots, it must bo below 0.
    it then splits the spline at the roots, and sets the bits below 0 to 0

    Parameters
    ----------
    pieces : list of np.ndarray
        A list of arrays representing cubic splines for each interval.
        Each array has the form [x1,x2,a,b,c,d].
        This represents the equation f(x) = a*x^3 + b*x^2 + c*x + d over the range [x1,x2]

    Returns
    -------
    list of np.ndarray
        A list of arrays representing cubic splines for each interval.
        Each array has the form [x1,x2,a,b,c,d].
        This represents the equation f(x) = a*x^3 + b*x^2 + c*x + d over the range [x1,x2]
        Some terms will have a,b,c and d all equal to 0, as otherwise they would lead to negative y values.
    """

    new_pieces=[]
    for piece in pieces:
        x1,x2,a,b,c,d=piece
        x=np.linspace(x1,x2,100)
        y=a*x**3+b*x**2+c*x+d
        if min(y)<0:

            roots = merge_sort([root for root in np.roots(piece[2:]) if np.isreal(root) and x1 <= root <= x2])
            p = [x1] + roots + [x2]
            for x1, x2 in zip(p, p[1:]):
                x = (x1 + x2) / 2
                y = a * x ** 3 + b * x ** 2 + c * x + d
                if y < 0:
                    new_pieces.append(np.array([x1, x2, 0, 0, 0, 0]))
                else:
                    new_pieces.append(np.array([x1, x2, a, b, c, d]))
        else:
            new_pieces.append(piece)
    return new_pieces