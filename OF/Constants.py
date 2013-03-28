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


"""
Commonly used constants are defined globally by this package.
"""

g = 9.81
"""
Gravity acceleration :math:`[g] = \\frac{m}{s^2}`.

:type: float
"""

water = {
    'nu' : 1.004e-6,
    'mu' : 1.002e-3,
    'rho': 1000
    }
"""
Properties of sweet water at :math:`T=20^\circ`

:type: dict
"""

turbulence = {
    'I' : 0.05,
    'Cmu': 0.09
    }
