from math import log,sqrt
from OF import Constants
from OF.Basic import FlowProperties
"""
This package contains various skin friction curves, that are used in naval
architecture. All definitions should be based on the Reynoldsnumber as well as
on the velocity and the Froude number.
"""

def forceCoeff(F,
        Swett,
        u=None,
        Re=None,
        Fr=None,
        **kwargs):
    """
    Calculates the force coefficient by

    ..math::

        C = \\frac{F}{0.5\\rho S_{wett} u^2}

    :param F: Force
    :type F: float
    :param Swett: Wetted surface area
    :type Swett: float
    :param u: Velocity
    :type u: float
    :param Re: Reynoldsnumber
    :type Re: float
    :param Fr: Froudenumber
    :type Fr: float

    :rtype: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    if not 'rho' in kwargs.iterkeys():
        rho = Constants.water['rho']
    else:
        rho = kwargs['rho']

    if Re:
        u = FlowProperties.Re(Re=Re,L=kwargs['L'])
    elif Fr:
        u = FlowProperties.Fr(Fr=Fr,L=kwargs['L'])


    return F/(0.5*rho*Swett*u**2)


