import random
from math import comb,sqrt,pi,exp
def sim_Bin(n,p):
    r=random.binomialvariate(n,p)
    return r

def ideal_Bin(n,r,p):
    return comb(n,r) * p**r * (1-p)**(n-r)

def sim_Geo(p):
    c=1
    while random.random()>p:
        c+=1
    return c

def ideal_Geo(r,p):
    if r == 0:
        return 0
    else:
        return p*(1-p)**(r-1)

def sim_Normal(mu,sigma):
    return random.normalvariate(mu,sigma)

def ideal_Normal(mu,sigma,r):
    return (1 / (sigma * sqrt(2 * pi))) * exp(-0.5 * ((r - mu) / sigma) ** 2)
