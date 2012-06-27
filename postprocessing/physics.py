#!/usr/bin/env python

import numpy

h=6.62617e-34				# J s Planck
k=1.380662e-23				# J/K Boltzmann
c=2.99792458e8				# m/s speed of light


def rjbt(radiance,frequency):
    """Returns the Rayleigh Jeans brightness temperature for a given
    radiances and frequency(Hz)"""
    return radiance*c**2/(2*frequency**2*k)


def vapour_P(T):
    """ Pvs = vapour_P(T) Calculates the saturated vapour pressure (Pa)
    of water using Hyland-Wexler eqns (ASHRAE Handbook) T in Kelvin!"""
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%CONSTANTS
    A = -5.8002206e3
    B = 1.3914993
    C = -4.8640239e-2
    D = 4.1764768e-5
    E = -1.4452093e-8
    F = 6.5459673
    #%%%%%%%%%%%%%%%;%%%%%%%%%%%
    
    
    Pvs = numpy.exp(A/T + B + C*T + D*T**2 + E*T**3 + F*numpy.log(T))
    return Pvs

def vapour_P_ice(T):
    """ Pvs = vapour_P_ice(T) Calculates the saturated vapour pressure (Pa)
    of water using the relation of List (1951). See JPL Clouds ATBD for
    reference."""
    Pvs=10**(-9.097*(273.16/T-1)-3.5665*numpy.log10(273.16/T)+0.8768*(1-T/273.16)+2.786)
    return Pvs

def psychrometer(tdb,twb,P=1.01325e5):
    """returns the relative humidity (wrt liquid water, between 0 and 1) given
    the dry bulb and wet-bulb temperature (in K)"""
    Wsdash = 0.62198*vapour_P(twb)/(P-vapour_P(twb));
    W = ((2501 - 2.381*(twb-273.15))*Wsdash - 1.006*(tdb-twb))/\
        (2502+1.805*(tdb-273.15)-4.186*(twb-273.15));
    Ws = 0.62198*vapour_P(tdb)/(P-vapour_P(tdb));
    mu = W/Ws;
    
    relhum = mu/(1-(1-mu)*(vapour_P(tdb)/P));
    return relhum

def wavelength2frequency(wavelength):
    """Converts wavelength (in meters) to frequency (in Hertz)
    """

    return c/wavelength

def vapour_PF(T):
    return vapour_P((T-32)/1.8+273.25)

def W_dewpt(dp):
    """dewpoint in F; returns humidity ratio kg H2O per kg dry air (equiv lb/lb)"""
    P = 101325
    pws = vapour_PF(dp)
    xw = pws/P
    w = 0.621945*xw*P/(P-xw*P)
    return w

def humidity_ratio(rh, T):
    """rh in range [0,1]; T in F; returns humidity ratio kg H2O per kg dry air (equiv lb/lb)"""
    P = 101325
    pws = vapour_PF(T)
    xws = pws/P
    xw = rh*xws
    w = 0.621945*xw*P/(P-xw*P)
    return w

def rh(w, T):
    """reversing humidity_ratio, above)"""
    P = 101325
    pws = vapour_PF(T)
    xws = pws/P
    xw = w/(0.621945+w)
    rh = xw/xws
    return rh

def enthalpy(W, T):
    """T in degF, return h in BTU/lb_da"""
    return 0.240*T + W*(1061 + 0.444*T)

def enthalpy_RH(RH, T):
    return enthalpy(humidity_ratio(RH, T), T)

def f2K(T):
    return (T-32)/1.8+273

def K2f(T):
    return (T-273)*1.8+32

def wet_bulb(RH, Tdb, low=-40, high=None):
    if RH < 0 or RH > 1:
        raise Exception("RH out of range: {0}".format(RH))
    if high==None:
        high = Tdb
    def wet_bulb_(RH, Tdb, low, high, err=0.001):
        while True:
            wb = (low+high)/2
            test = psychrometer(Tdb, wb)
            if abs(RH-test) < err:
                return wb
            else:
                if test < RH:
                    low = wb
                else:
                    high = wb
    return K2f(wet_bulb_(RH, f2K(Tdb), f2K(low), f2K(high)))


r22_Ts = [-100, -90, -80, -70, -60, -50, -48, -46, -44, -42, -40.81, -40, -38, -36, -34, -32, -30, -28, -26, -24, -22, -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 65, 70, 75, 80, 85, 90, 95, 96.15]

r22_Ps = [0.00201, 0.00481, 0.01037, 0.02047, 0.03750, 0.06453, 0.07145, 0.07894, 0.08705, 0.09580, 0.10132, 0.10523, 0.11538, 0.12628, 0.13797, 0.15050, 0.16389, 0.17819, 0.19344, 0.20968, 0.22696, 0.24531, 0.26479, 0.28543, 0.30728, 0.33038, 0.35479, 0.38054, 0.40769, 0.43628, 0.46636, 0.49799, 0.53120, 0.56605, 0.60259, 0.64088, 0.68095, 0.72286, 0.76668, 0.81244, 0.86020, 0.91002, 0.96195, 1.01600, 1.07240, 1.13090, 1.19190, 1.25520, 1.32100, 1.38920, 1.46010, 1.53360, 1.60980, 1.68870, 1.77040, 1.85510, 1.94270, 2.03330, 2.12700, 2.22390, 2.32400, 2.42750, 2.70120, 2.99740, 3.31770, 3.66380, 4.03780, 4.44230, 4.88240, 4.99000]

def R22_Tsat(Psat):
    return numpy.interp(Psat, r22_Ps, r22_Ts)

def R22_Psat(Tsat):
    return numpy.interp(Tsat, r22_Ts, r22_Ps)
