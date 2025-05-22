import random
from math import comb,sqrt,pi,exp

def sim_bin(n, p):
    r=random.binomialvariate(n,p)
    return r

def ideal_bin(n, r, p):
    return comb(n,r) * p**r * (1-p)**(n-r)

def sim_geo(p):
    c=1
    while random.random()>p:
        c+=1
    return c

def ideal_geo(r, p):
    if r == 0:
        return 0
    else:
        return p*(1-p)**(r-1)

def sim_normal(mu, sigma):
    return random.normalvariate(mu,sigma)

def ideal_normal(mu, sigma, r):
    return (1 / (sigma * sqrt(2 * pi))) * exp(-0.5 * ((r - mu) / sigma) ** 2)

def calc_bin(op, x1, n, p, x2=None):

    if op == "<":
        return sum(ideal_bin(n, i, p) for i in range(x1))
    if op == ">":
        return 1-sum(ideal_bin(n, i, p) for i in range(x1 + 1))
    if op == "≤":
        return sum(ideal_bin(n, i, p) for i in range(x1+1))
    if op == "≥":
        return 1-sum(ideal_bin(n, i, p) for i in range(x1))

    if op == "=":
        return ideal_bin(n,x1,p)
    if op == "< <":
        return sum(ideal_bin(n, i, p) for i in range(x1+1,x2))
    if op == "≤ ≤":
        return sum(ideal_bin(n, i, p) for i in range(x1,x2+1))

def backwards_calc_bin (op,n,p,pp):
    if op == "<":
        k=0
        while calc_bin(op,k,n,p)<=pp:
            k+=1
        return k-1
    if op == "≤":
        k=0
        while calc_bin(op,k,n,p)<=pp:
            k+=1
        return k-1
    if op == "≥":
        k=0
        while calc_bin(op,k,n,p)>=pp:
            k+=1
        return k-1
    if op == ">":
        k=0
        while calc_bin(op,k,n,p)>=pp:
            k+=1
        return k-1

def calc_geo(op, x1, p, x2=None):

    if op == "<":
        return sum(ideal_geo(i, p) for i in range(x1))
    if op == ">":
        return 1-sum(ideal_geo(i, p) for i in range(x1 + 1))
    if op == "≤":
        return sum(ideal_geo(i, p) for i in range(x1+1))
    if op == "≥":
        return 1-sum(ideal_geo(i, p) for i in range(x1))

    if op == "=":
        return ideal_geo(x1,p)
    if op == "< <":
        return sum(ideal_geo(i, p) for i in range(x1+1,x2))
    if op == "≤ ≤":
        return sum(ideal_geo(i, p) for i in range(x1,x2+1))

def backwards_calc_geo (op,p,pp):
    if op == "<":
        k=0
        while calc_geo(op,k,p)<=pp:
            k+=1
        return k-1
    if op == "≤":
        k=0
        while calc_geo(op,k,p)<=pp:
            k+=1
        return k-1
    if op == "≥":
        k=0
        while calc_geo(op,k,p)>=pp:
            k+=1
        return k-1
    if op == ">":
        k=0
        while calc_geo(op,k,p)>=pp:
            k+=1
        return k-1