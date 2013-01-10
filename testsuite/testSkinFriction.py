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
