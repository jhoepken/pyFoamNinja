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
