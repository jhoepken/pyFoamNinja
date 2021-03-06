#Copyright (C) 2013 Jens Hoepken

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


from math import log,sqrt

from numpy import arange
from numpy import log10

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

    try:
        return 0.075/((log(Re,10)-2)**2)
    except TypeError:
        return 0.075/((log10(Re)-2)**2)

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
        
    return 0.066/((log(Re,10)-2.03)**2)

def schoenherr(**kwargs):
    """
    Calculates the viscous drag coefficient :math:`C_{F0}` for the skin friction
    according to the Schoenherr line.

    ..math::

        \\frac{0.242}{\sqrt{C_F}} = \log_{10} (C_F Re)

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

    iteration = 100.0

    for CdI in arange(0.001,0.007,0.00001):
        if abs(0.242/sqrt(CdI) - log(CdI*Re,10)) < iteration:
            iteration = 0.242/sqrt(CdI) - log(CdI*Re,10)
            Cd = CdI
        else:
            return Cd
    return 0.0

