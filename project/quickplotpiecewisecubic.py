import matplotlib.pyplot as plt
import numpy as np

def plotpieces(points,pieces):

    for point in points:
        plt.plot(point[0],point[1],'ro')

    for piece in pieces:
        lower,upper,a,b,c,d,=piece
        x=np.linspace(lower,upper,50)
        y=np.maximum(a*x**3 + b*x**2 + c*x + d,0)
        #y=a*x**3 + b*x**2 + c*x + d

        plt.plot(x,y)
    plt.show()
if __name__ == '__main__':
    plotpieces([(0,0),(1,1),(1,2),(2,9)],np.array([[0,1,1,0,0,0],[1,2,1,0,0,1]]))