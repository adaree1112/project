from matplotlib import pyplot as plt

from quickplotpiecewisecubic import plotpieces

import numpy as np

def piecewise_cubic_spline(points):

    points = sorted(points, key=lambda p: p[0])
    print(points)
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
    """
    ## f1'(x1)=0
    matrix[-2][0] = 3 * points[0][0]**2
    matrix[-2][1] = 2 * points[0][0]
    matrix[-2][2] = 1

    ## f(n-1))'(x(n-1))=0
    matrix[-1][-4] = 3 * points[-1][0]**2
    matrix[-1][-3] = 2 * points[-1][0]
    matrix[-1][-2] = 1
"""
    inversematrix=np.linalg.inv(matrix)



    # print(matrix)
    # print(matb)
    print(np.matmul(inversematrix,matb))
    coefficientmatrix=np.matmul(inversematrix,matb)

    pieces=[[points[i][0],points[i+1][0],coefficientmatrix[4*i][0],coefficientmatrix[4*i+1][0],coefficientmatrix[4*i+2][0],coefficientmatrix[4*i+3][0]]
            for i in range(n)]

    return pieces

def find_roots(piece):
    x1,x2,a,b,c,d=piece
    roots = [root for root in np.roots(piece[2:]) if np.isreal(root) and x1 <= root <= x2]
    print(roots)




def deal_with_negatives(pieces):
    for piece in pieces:
        x1,x2,a,b,c,d=piece
        x=np.linspace(x1,x2,100)
        y=a*x**3+b*x**2+c*x+d
        if any(y<0):
            return x1,x2

def integratecubic(x1,x2,a,b,c,d):
    return a*(x2**4-x1**4)/4 + b*(x2**3-x1**3)/3 + c*(x2**2-x1**2)/2+d*(x2-x1)

def integratepiecewisecubic(pieces):
    area=0
    for piece in pieces:
        area+=integratecubic(*piece)
    return area

def normalisepiecewisecubic(pieces):
    points=[]
    for piece in pieces:
        x1=piece[0]
        x2=piece[1]
        a=piece[2]
        b=piece[3]
        c=piece[4]
        d=piece[5]

        y1=a*x1**3+b*x1**2+c*x1+d
        y2=a*x2**3+b*x2**2+c*x2+d
        points+=[(x1,y1),(x2,y2)]
    points=list(set(points))

    area=integratepiecewisecubic(pieces)
    areascalefactor=1/area

    points=[(point[0],areascalefactor*point[1])for point in points]
    return points,piecewise_cubic_spline(points)


points=[(1,0), (2, 0.25), (3, 2), (4, 1)]

# #print(piecewise_cubic_spline(points))
pieces=piecewise_cubic_spline(points)
plotpieces(points,pieces)
print(find_roots(pieces[0]))
# pieces=[[2,3,-0.75,4.5,-6.25,3.5],[3,4,0.75,-9,34.25,-37.0]]
# points,pieces=normalisepiecewisecubic(pieces)
# plotpieces(points,pieces)
# print(integratepiecewisecubic(pieces))