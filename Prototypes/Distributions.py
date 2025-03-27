import random

def sim_Bin(n,p):
    return random.binomialvariate(n,p)

def sim_Geo(p):
    c=1
    while random.random()<p:
        c+=1
    return

def sim_Normal(mu,sigma):
    return random.normalvariate(mu,sigma)
