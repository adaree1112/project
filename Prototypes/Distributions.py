import random
from math import comb
def sim_Bin(n,p):
    r=random.binomialvariate(n,p)
    return r

def ideal_Bin(n,r,p):
    return comb(n,r) * p**r * (1-p)**(n-r)

def sim_Geo(p):
    c=1
    while random.random()<p:
        c+=1
    return

def sim_Normal(mu,sigma):
    return random.normalvariate(mu,sigma)
