
def piecewise_linear (points):
    output = []
    for point,nextpoint in zip(points,points[1:]):
        if point == nextpoint:
            continue
        x1,y1=point
        x2,y2=nextpoint
        m=(y2-y1)/(x2-x1)
        c=y1-m*x1
        output.append((point[0],nextpoint[0],m,c))
    return output

def normalise_piecewise_linear (pieces):
    area=0
    for piece in pieces:
        x1,x2,m,c=piece

        y1=m*x1+c
        y2=m*x2+c

        trapeziumarea = .5*(y1+y2)*(x2-x1)
        area+=trapeziumarea

    areascalefactor=1/area

    points=[]
    for piece in pieces:
        x1,x2,m,c=piece

        y1=m*x1+c
        y2=m*x2+c

        newy1=areascalefactor*y1
        newy2=areascalefactor*y2

        points.append((x1,newy1))
        points.append((x2,newy2))

    output=piecewise_linear(points)
    return output

print(pieces:=piecewise_linear([(1, 1), (2, 2), (3,1)]))
print(normalise_piecewise_linear(pieces))