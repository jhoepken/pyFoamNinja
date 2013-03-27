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
from OF.Basic import FlowProperties

class KnownValues(unittest.TestCase):

    # Known velocites and their respective Froude numbers for a reference length
    # of 1m and a gravity of 9.81 m/s**2
    vFr = ( 
            (1.0, 0.31927542840705048),
            (2.0, 0.63855085681410095),
            (200.0, 63.855085681410088)
        )

    # Known velocites and their respective Reynodls numbers for a reference length
    # of 1m, a gravity of 9.81 m/s**2 and a kinematic viscosity as defined in
    # the OF.Constants for water
    vRe = (
            (1.0, 996015.93625498004),
            (2.0, 1992031.8725099601),
            (200.0, 199203187.25099599)
        )

    def testVelToFr(self):
        """
        Tests the conversion from velocity to Froude number
        """
        for vel,Froude in self.vFr:
            result = FlowProperties.Fr(u=vel,L=1.0,nu=Constants.water['nu'])
            self.assertEqual(Froude, result)

    def testFrToVel(self):
        """
        Tests the conversion from Froude nubmer to velocity
        """
        for vel,Froude in self.vFr:
            result = FlowProperties.Fr(Fr=Froude,L=1.0,nu=Constants.water['nu'])
            self.assertEqual(vel, result)

    def testVelToRe(self):
        """
        Tests the conversion from velocity to Reynoldsnumber
        """
        for vel,Reynolds in self.vRe:
            result = FlowProperties.Re(u=vel,L=1.0,nu=Constants.water['nu'])
            self.assertEqual(Reynolds, result)
            
    def testReToVel(self):
        """
        Tests the conversion from Reynoldsnumber to velocity
        """
        for vel,Reynolds in self.vRe:
            result = FlowProperties.Re(Re=Reynolds,L=1.0,nu=Constants.water['nu'])
            self.assertEqual(vel, result)
            


if __name__ == "__main__":
    unittest.main()
