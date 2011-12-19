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
