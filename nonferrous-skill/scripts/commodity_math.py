"""Unit-explicit helpers; parameters are caller-provided facts/assumptions."""
import math
def quarterly(q_cum,p_cum,c_cum,q_prior,p_prior,c_prior):
    q=q_cum-q_prior
    if q<=0: raise ValueError('Non-positive incremental sales; inspect scope')
    return q,(q_cum*p_cum-q_prior*p_prior)/q,(q_cum*c_cum-q_prior*c_prior)/q
def bridge(q0,p0,c0,q1,p1,c1,factor=1):
    parts={'volume':(q1-q0)*(p0-c0)*factor,'price':q1*(p1-p0)*factor,'cost':-q1*(c1-c0)*factor}
    assert math.isclose(sum(parts.values()),(q1*(p1-c1)-q0*(p0-c0))*factor,rel_tol=1e-10,abs_tol=.01)
    return parts
def recovered_metal(ore_tonnes,grade_fraction,recovery_fraction,ownership=1):
    if ore_tonnes<0 or any(not 0<=x<=1 for x in [grade_fraction,recovery_fraction,ownership]):raise ValueError('Invalid units/range')
    return ore_tonnes*grade_fraction*recovery_fraction*ownership
if __name__=='__main__':
    q,p,c=quarterly(40663,995.77,356.96,27424,1034.09,347.30)
    result=bridge(27424/2,1034.09,347.30,q,p,c,1000)
    assert recovered_metal(1000000,.01,.9,.4)==3600
    print({'quarterly':(q,p,c),'bridge':result})
