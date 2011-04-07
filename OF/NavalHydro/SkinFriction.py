from math import log,sqrt
from OF import Constants
from OF.Basic import FlowProperties
"""
This package contains various skin friction curves, that are used in naval
architecture. All definitions should be based on the Reynoldsnumber as well as
on the velocity and the Froude number.
"""

def ittc57(**kwargs):
    """
    Calculates the viscous drag coefficient :math:`C_D` for the skin friction 
    according to the ITTC'57 correlation line, which already accounts for 
    approximately 12% of pressure induced friction and should therefore 
    overestimate the skin friction of e.g. a plain turbulent plate.

    ..math::

        C_F = \\frac{0.075}{(\log Re - 2)^2}

    It is not necessary to hand a Reynoldsnumber to the function. If a velocity
    or Froudenumber and a reference length is passed, the Reynoldsnumber is
    derived accordingly.

    :param Re: Reynoldsnumber
    :type Re: float
    :param Fr: Froudenumber
    :type Fr: float
    :param u: Velocity :math:`[\\frac{m}{s}]`
    :type u: float
    :param L: Reference length :math:`[m]`
    :type L: float

    :rtype: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """
    if 'Re' in kwargs.iterkeys():
        Re = kwargs['Re']
    else:
        u,Fr,Re = FlowProperties.uFrRe(**kwargs)

    return 0.075/((log(Re)-2)**2)

def huges(**kwargs):
    """
    Calculates the viscous drag coefficient :math:`C_{F0}` for the skin friction
    according to the Hughes line. This is not used on a regular basis by the
    model basins, but for simulations dealing with the turbulent flow over e.g.
    a flat plate, this curve gives more accurate results to compare the CFD
    results to.

    ..math::

        C_{F0} = \\frac{0.066}{(\log Re - 2.03)^2}

    It is not necessary to hand a Reynoldsnumber to the function. If a velocity
    or Froudenumber and a reference length is passed, the Reynoldsnumber is
    derived accordingly.

    :param Re: Reynoldsnumber
    :type Re: float
    :param Fr: Froudenumber
    :type Fr: float
    :param u: Velocity :math:`[\\frac{m}{s}]`
    :type u: float
    :param L: Reference length :math:`[m]`
    :type L: float

    :rtype: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    if 'Re' in kwargs.iterkeys():
        Re = kwargs['Re']
    else:
        u,Fr,Re = FlowProperties.uFrRe(**kwargs)
        
    return 0.066/((log(Re)-2.03)**2)
