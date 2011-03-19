from math import log,sqrt
from OF import Constants
from OF.Basic import Utilities,FlowProperties
"""
This package contains various skin friction curves, that are used in naval
architecture. All definitions should be based on the Reynoldsnumber as well as
on the velocity and the Froude number.
"""

def cd(F,
        Swett,
        v=None,
        Re=None,
        Fr=None):
    pass


def ittc57(Re=None,
            v=None,
            Fr=None,
            L=None,
            nu=1e-6):
    """
    Calculates the viscous drag coefficient :math:`C_D` for the skin friction 
    according to the ITTC'57 correlation line, which already accounts for 
    approximately 12% of pressure induced friction and should therefore 
    overestimate the skin friction of e.g. a plain turbulent plate.

    :param Re: Reynoldsnumber
    :type Re: float
    :param v: Velocity :math:`[\\frac{m}{s}]`
    :type v: float
    :param L: Reference length :math:`[m]`
    :type L: float
    :param nu: Kinematic viscosity (Default = :math:`10^{-6}`)
    :type nu: float

    :rtype: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """
    # Calculate the number of undefined parameters. Maybe this should be
    # improved by using the argument pointers of python (kwargs**) etc.
    pCount = [v,Re,Fr].count(None)

    if not v and not Re and not Fr:
        raise ValueError("Neither v nor Re and Fr have been provided")
    elif pCount < 2 :
        raise ValueError("Too many velocity definitions (Re, v, Fr)")

    if v:
        if not L:
            raise ValueError("A length has to be passed, as the Reynoldsnumber \
                             needs to be computed")
        Re = FlowProperties.Re(v=v, L=L)
    elif Re:
        Re = float(Re)

    elif Fr:
        v = FlowProperties.Fr(Fr=Fr,L=L)
        Re = FlowProperties.Re(v=v, L=L)

    return 0.075/((log(Re)-2)**2)


