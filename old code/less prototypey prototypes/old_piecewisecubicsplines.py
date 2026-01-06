import matplotlib.pyplot as plt

import numpy as np

def piecewise_cubic_spline(points):

    points = sorted(points, key=lambda p: p[0])
    #print(points)
    n=len(points)-1

    matrix=np.zeros((4*n,4*n))
    matb=np.zeros((4*n,1))

    ## f(X1) = y1, f(X2)=y2
    for i in range(n):

        matrix[2*i][4*i+0] = points[i][0]**3
        matrix[2*i][4*i+1] = points[i][0]**2
        matrix[2*i][4*i+2] = points[i][0]**1
        matrix[2*i][4*i+3] = points[i][0]**0
        matb[2*i][0]=points[i][1]

        matrix[2*i+1][4*i+0] = points[i+1][0] ** 3
        matrix[2*i+1][4*i+1] = points[i+1][0] ** 2
        matrix[2*i+1][4*i+2] = points[i+1][0] ** 1
        matrix[2*i+1][4*i+3] = points[i+1][0] ** 0
        matb[2*i+1][0] = points[i+1][1]

    ## f1'(x2)-f2'(x2)=0
    for i in range(n-1):
        matrix[2*n+i][4*i+0] = 3*points[i+1][0]**2
        matrix[2*n+i][4*i+1] = 2*points[i+1][0]**1
        matrix[2*n+i][4*i+2] = 1*points[i+1][0]**0

        matrix[2*n+i][4*i+4] = -3*points[i+1][0]**2
        matrix[2*n+i][4*i+5] = -2*points[i+1][0]**1
        matrix[2*n+i][4*i+6] = -1*points[i+1][0]**0
    ## f1''(x2)-f2''(x2)=0
    for i in range(n-1):
        matrix[2*n+(n-1)+i][4*i+0] = 6*points[i+1][0]**1
        matrix[2*n+(n-1)+i][4*i+1] = 2*points[i+1][0]**0

        matrix[2*n+(n-1)+i][4*i+4] = -6*points[i+1][0]**1
        matrix[2*n+(n-1)+i][4*i+5] = -2*points[i+1][0]**0
    #"""
    ## f1''(x1)=0
    matrix[-2][0]=6*points[0][0]
    matrix[-2][1]=2
    ## f(n-1))''(x(n-1))=0
    matrix[-1][-4]=6*points[-1][0]
    matrix[-1][-3]=2

    coefficientmatrix=np.linalg.solve(matrix,matb)
    pieces=[np.array([points[i][0],points[i+1][0],coefficientmatrix[4*i][0],coefficientmatrix[4*i+1][0],coefficientmatrix[4*i+2][0],coefficientmatrix[4*i+3][0]])
            for i in range(n)]
    pieces=dealwithnegatives(pieces)
    return pieces

def piecewise_linear(points):
    points = sorted(points, key=lambda p: p[0])

    output = []
    for point, nextpoint in zip(points, points[1:]):
        if point == nextpoint:
            continue
        x1, y1 = point
        x2, y2 = nextpoint
        c = (y2 - y1) / (x2 - x1)
        d = y1 - c * x1
        output.append(np.array([x1, x2, 0, 0, c,d]))
    return output

def dealwithnegatives(pieces):
    newpieces=[]
    for piece in pieces:
        x1,x2,a,b,c,d=piece
        x=np.linspace(x1,x2,100)
        y=a*x**3+b*x**2+c*x+d
        if min(y)<0:

            roots = sorted([root for root in np.roots(piece[2:]) if np.isreal(root) and x1 <= root <= x2])
            p = [x1] + roots + [x2]
            for x1, x2 in zip(p, p[1:]):
                x = (x1 + x2) / 2
                y = a * x ** 3 + b * x ** 2 + c * x + d
                if y < 0:
                    newpieces.append(np.array([x1, x2, 0, 0, 0, 0]))
                else:
                    newpieces.append(np.array([x1, x2, a, b, c, d]))
        else:
            newpieces.append(piece)
    return newpieces

def integratefullpiecewisecubic(pieces):
    area=0
    for piece in pieces:
        x1,x2,a,b,c,d=piece
        area+=a*(x2**4-x1**4)/4 + b*(x2**3-x1**3)/3 + c*(x2**2-x1**2)/2+d*(x2-x1)
    return area

def integratepiecewise(pieces,A=None,B=None):
    def integrate(A,B,piece):
        a,b,c,d=piece[2:]
        return a*(B**4-A**4)/4 + b*(B**3-A**3)/3 + c*(B**2-A**2)/2+d*(B-A)
    total=0
    for p,piece in enumerate(pieces):
        x1,x2,a,b,c,d=piece
        if A and B:
            lowerbound=max(A,x1)
            upperbound=min(B,x2)
        else:
            lowerbound=x1
            upperbound=x2
        if lowerbound < upperbound:
            total+=integrate(lowerbound,upperbound,piece)
    return total


def normalisepiecewisecubic(points,pieces):
    area=integratepiecewise(pieces)
    k=1/area
    points=[(point[0],k*point[1]) for point in points]
    pieces=[np.concatenate((piece[:2],k * piece[2:])) for piece in pieces]
    return points,pieces

def plotpieces(points,pieces):
    for point in points:
        plt.plot(point[0], point[1], 'ro')

    for piece in pieces:
        lower,upper,a,b,c,d,=piece
        x=np.linspace(lower,upper,50)
        #y=np.maximum(a*x**3 + b*x**2 + c*x + d,0)
        y=a*x**3 + b*x**2 + c*x + d

        plt.plot(x,y)
    plt.show()


if __name__=='__main__':
    print(integratepiecewise(2.5,3.5,[[2,3,.75,-4.5,7.25,.5],[3,4,-.75,9,-33.25,41]]))

    quit()
    points=[(1,0), (2, 0.25), (3, 2), (4, 1)]

    #print(piecewise_cubic_spline(points))
    pieces=piecewise_cubic_spline(points)#+piecewise_linear(points)
    #pieces=piecewise_linear(points)
    plotpieces(points,pieces)

    points,pieces=normalisepiecewisecubic(points,pieces)
    plotpieces(points,pieces)
    print(integratefullpiecewisecubic(pieces))