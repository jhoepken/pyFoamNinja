from os import listdir
from os.path import join

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from OF import Settings

class case(SolutionDirectory):
    """
    Inherits all function from
    :class:`PyFoam.RunDictionary.SolutionDirectory` and reads some
    properties from the case on initialisation.

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    turbulenceModel = None
    """
    Stores the name of the employed turbulence model

    :type: string
    """

    inletPatch = None
    """
    Stores the name of the inlet patch

    :type: string
    """

    inletVelocity = 0.0
    """
    Stores the inlet velocity as a vector

    :type: tuple
    """

    def __init__(
                    self,
                    name,
                    archive=None,
                    paraviewLink=True,
                    parallel=False,
                    region=None,
                    **kwargs
                ):
        """
        :param name: Name of the solution directory
        :type name: string
        """
        # Run the parent constructor
        SolutionDirectory.__init__(
                                    self,
                                    name,
                                    archive=archive,
                                    paraviewLink=paraviewLink,
                                    parallel=parallel,
                                    region=region
                                    )

        # Get the used turbulence model
        self.turbulenceModel = self.getDictionaryContents(
                                                self.constantDir(),
                                                'RASProperties'
                                            )['RASModel']

        if 'inletPatch' in kwargs.iterkeys():
            self.inletPatch = kwargs['inletPatch']
        else:
            self.inletPatch = Settings.inletPatch

        self.inletVelocity = self.getDictionaryContents(self.first,'U')\
                            ['boundaryField'][self.inletPatch]['value'].val
                        
