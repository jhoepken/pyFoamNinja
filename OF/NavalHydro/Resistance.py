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


