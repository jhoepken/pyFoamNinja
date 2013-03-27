#!/usr/bin/env python
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


import unittest
from OF import Constants
from OF.Basic import Turbulence

class KnownValues(unittest.TestCase):

    uInf_kEpsilonOmega = (
            ({'u':1.0, 'I': 0.05, 'l':0.005}, {'k':3.75e-3, 'epsilon':7.546729434e-3, 'omega':22.36067978}),
            ({'u':10.0, 'I': 0.05, 'l':0.005}, {'k':0.375, 'epsilon':7.546729424, 'omega':223.60679775}),
            ({'u':5.0, 'I': 0.05, 'l':42.0}, {'k':0.09375, 'epsilon':1.123025212e-4, 'omega':0.013309928})
            )

    def testInitField(self):
        """
        Tests the conversion from velocity to Froude number
        """
        for input, output in self.uInf_kEpsilonOmega:
            result = Turbulence.initField(
                    input['u'],
                    input['l'],
                    I = input['I']
                    )
            self.assertAlmostEqual(output['k'], result['k'])
            self.assertAlmostEqual(output['epsilon'], result['epsilon'])
            self.assertAlmostEqual(output['omega'], result['omega'])


if __name__ == "__main__":
    unittest.main()
