
def piecewise_linear (points):
    output = []
    for point,nextpoint in zip(points,points[1:]):
        x1=point[0]
        y1=point[1]
        x2=nextpoint[0]
        y2=nextpoint[1]
        m=(y2-y1)/(x2-x1)
        c=y1-m*x1
        output.append((point[0],nextpoint[0],m,c))
    return output

def normalise_piecewise_linear (pieces):
    output = []
    area=0
    for piece in pieces:
        x1=piece[0]
        x2=piece[1]
        m=piece[2]
        c=piece[3]
        y1=m*x1+c
        y2=m*x2+c
        trapeziumarea = .5*(y1+y2)*(x2-x1)
        area+=trapeziumarea

    areascalefactor=1/area
    lengthscalefactor=areascalefactor**.5
    print(area,areascalefactor,lengthscalefactor)

    points=[]
    for piece in pieces:
        x1=piece[0]
        x2=piece[1]
        m=piece[2]
        c=piece[3]

        y1=m*x1+c
        y2=m*x2+c

        newy1=areascalefactor*y1
        newy2=areascalefactor*y2

        points.append((x1,newy1))
        points.append((x2,newy2))

    output=piecewise_linear(points)
    return output

print(pieces:=piecewise_linear([(1, 1), (2, 2), (3, 1)]))



print(normalise_piecewise_linear(pieces))