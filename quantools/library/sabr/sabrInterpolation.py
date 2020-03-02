from pysabr import Hagan2002LognormalSABR

def sabrInterpolation(f=0.025, shift=0.03, t=1., v_atm_n=0.0040,
                              beta=0.5, rho=-0.2, volvol=0.30,k=0.025,type = "LN"):
    sabr =  Hagan2002LognormalSABR(f=0.025, shift=0.03, t=1., v_atm_n=0.0040,
                              beta=0.5, rho=-0.2, volvol=0.30)
    if type == "LN":
        return sabr.lognormal_vol(k)

    return sabr.normal_vol(k)*100
