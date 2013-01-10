from os.path import join
from math import sqrt

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from OF import Constants
"""
This package contains some untilities to handle the turbulence modelling and
provide easy access to the initialisation of the field variables.
"""

class initField():
    """
    Provides access to the initialisation of the turbulence related field
    variables. The values for :math:`k`, :math:`\epsilon` and :math:`\omega` are
    calculated according to the Fluent handbook, as no **real** information on
    the derivation have been found. Unfortunately the original paper of Menter
    was not available.


    ..todo::
        The variables k, epsilon and omega may be deleted and the data stored in
        the vars dictionary. As the __getitem__ method provides easy access to
        the data, this should be sufficiently convenient.

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    uInf = 0
    l = 0
    k = 0
    epsilon = 0
    omega = 0

    vars = {}

    def __init__(
                self,
                uInf,
                l,
                **kwargs
                ):
        """
        :param uInf: Freestream velocity
        :type uInf: float
        :param l: Reference length (0.007*D_h)
        :type l: float
        """
        self.uInf = uInf
        self.l = l
        
        # Use the globally defined turbulent intensity, if no such parameter has
        # been passed.
        try:
            self.I = kwargs['I']
        except KeyError:
            self.I = Constants.turbulence['I']

        ## Initialise k and epsilon
        # Data gathered from fluent handbook for channel flows based
        # on hydraulic diameter.

        # Turbulent kinetic energy
        self.k = 1.5*(self.uInf*self.I)**2

        # Turbulent kinetic energy dissipation rate
        self.epsilon = Constants.turbulence['Cmu']**(3.0/4.0)*(self.k**(3.0/2.0)/l)

        # Turbulent frequency
        self.omega = self.k**(1.0/2.0)/(Constants.turbulence['Cmu']**(1.0/4.0)*l)

        self.vars['k'] = self.k
        self.vars['epsilon'] = self.epsilon
        self.vars['omega'] = self.omega


    def __getitem__(self,key):
        return self.vars[key]

class initFieldFoam(initField):
    """
    This class does exectly the same as :class:`~OF.Basic.Turbulence.initField`,
    but has the ability to write the respective values to the particular
    boundary patches and fields in OpenFOAM case.

    Depending on the turbulence model used, different field values are updated
    by the function.

    ..seealso: 
        
        :class:`~OF.Basic.Turbulence.initField`
    """

    def __init__(
                self,
                case,
                uInf,
                l,
                **kwargs
                ):
        """
        :param case: OpenFOAM case
        :type case: :class:`~OF.Basic.Case.case`

        :param uInf: Freestream velocity
        :type uInf: float
        :param l: Reference length
        :type l: float
        """

        # Run parent constructor
        initField.__init__(
                            self,
                            uInf,
                            l,
                            **kwargs
                            )
        self.case = case

        # Create a list of boundary files, that need to be set.
        self.turbBC = []
        if self.case.turbulenceModel == 'kEpsilon':
            self.turbBC = ['k','epsilon']
        elif self.case.turbulenceModel == 'kOmega':
            self.turbBC = ['k','omega']
        elif 'kOmegaSST' in self.case.turbulenceModel:
            self.turbBC = ['k','omega']


    def write(self):
        """
        Updates the values for the turbulent flow properties and writes all
        **turbulent** boundary files. Wallfunctions, if used, are updated as
        well.
        """
        for bcI in self.turbBC:
            for inletPatchI in self.case.inletPatch:
                bcFile = ParsedParameterFile(
                                            join(
                                                self.case.name,
                                                self.case.first,
                                                bcI
                                                )
                                            )
                # Set the internal field and the inlet patch at first
                bcFile['internalField'] = "uniform %f" %(self.vars[bcI])
                bcFile['boundaryField'][inletPatchI]['value'] = \
                                                "uniform %f" %(self.vars[bcI])

                # Update the wallfunctions if they are used
                for patchI in bcFile['boundaryField']:

                    if "allFunction" in bcFile['boundaryField'][patchI]['type']:
                        bcFile['boundaryField'][patchI]['value'] = \
                                                "uniform %f" %(self.vars[bcI])

                # Write the current boundary file
                bcFile.writeFile()


