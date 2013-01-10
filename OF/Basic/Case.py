from os import listdir
from os.path import join,split
from re import compile,findall

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from OF import Settings
from OF.PostProcessing import DataFile    
from OF.NavalHydro import Resistance
from OF.Basic import Utilities, FlowProperties

class case(SolutionDirectory):
    """
    Inherits all function from
    :class:`PyFoam.RunDictionary.SolutionDirectory` and reads some
    properties from the case on initialisation.

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    Re = 0.0
    """
    Stores the Reynoldsnumber

    :type: float
    """

    Fr = 0.0
    """
    Stores the Froudenumber

    :type: float
    """

    uInf = 0.0

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

    forces = None
    """
    Stores the relative path to the forces.dat

    :type: OF.PostProcessing.DataFile
    """

    shortCasePath = None
    """
    Stores an abbreviated version of the case name, that is calculated from the
    working directory.

    :type: string
    """

    resistances = {'CF':None,'CT':None,'RF':None,'RT':None}
    """
    Stores the forces and coefficients in the common naval architecture
    notation, as a dict. The type is the key. 
    resistances['CF'] = ..

    :type: numpy array
    """

    t = None
    """
    Stores the time line for each timestep

    :type: numpy array
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
        self.resistances = {'CF':None,'CT':None,'RF':None,'RT':None}

        # Get the used turbulence model
        self.turbulenceModel = self.getDictionaryContents(
                                                self.constantDir(),
                                                'RASProperties'
                                            )['RASModel']

        ###############################
        # Process optional parameters #
        ###############################
        if 'inletPatch' in kwargs.iterkeys():
            self.inletPatch = kwargs['inletPatch']
        else:
            self.inletPatch = Settings.inletPatch

        if 'L' in kwargs.iterkeys():
            self.L = kwargs['L']
        else:
            self.L = 1.0

        if 'A' in kwargs.iterkeys():
            self.A = kwargs['A']
        else:
            self.A = 1.0

        if 'direction' in kwargs.iterkeys():
            self.direction = kwargs['direction']
        else:
            self.direction = -1

        self.updateInletVelocity()
        self.forces = self.createDataFile()

        try:
            self.calculateCoeffs()
        except TypeError:
            pass
        except ValueError:
            pass

        self.getShortCasePath()
        self.shortCaseName = split(self.name)[1]


    def calculateCoeffs(self):
        """
        If forces exist, the respective coefficients are calculated accordingly.
        Otherwise a ValueError is raised.

        :param L: Reference length
        :type L: float
        :param A: Reference area
        :type A: float
        """
        self.uInf = Utilities.mag(self.inletVelocity)
        self.Re = FlowProperties.Re(L=self.L,u=self.uInf)
        self.Fr = FlowProperties.Fr(L=self.L,u=self.uInf)

        if self.forces:
            self.t = self.forces[0]
            self.resistances['RF'] = self.direction*self.forces[abs(self.direction)+3]
            self.resistances['RT'] = self.resistances['RF'] +\
                                    self.direction*self.forces[abs(self.direction)]
            self.resistances['CF'] = Resistance.forceCoeff(self.resistances['RF'],
                                                        self.A,u=self.uInf)
            self.resistances['CT'] = Resistance.forceCoeff(self.resistances['RT'],
                                                        self.A,u=self.uInf)
        else:
            raise ValueError

    def getShortCasePath(self):
        out = []
        for fI in self.name.split('/'):
            if fI == 'run':
                out.append(fI)
            elif len(out) > 0:
                out.append(fI)

        self.shortCasePath = "/".join(out[1:])


    def updateInletVelocity(self):
        inletFound = False
        with open(join(self.name,self.first,'U'),'r') as bc:
            for line in bc:
                if self.inletPatch in line:
                    inletFound = True
                if inletFound:
                    if "uniform" in line:
                        vIn = line
                        break

        numberRe = compile(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
        self.inletVelocity = [float(uI) for uI in findall(numberRe,vIn)]
        self.uInf = Utilities.mag(self.inletVelocity)
        self.Re = FlowProperties.Re(L=self.L,u=self.uInf)
        self.Fr = FlowProperties.Fr(L=self.L,u=self.uInf)


            #self.inletVelocity = self.getDictionaryContents(self.first,'U')\
                        #['boundaryField'][self.inletPatch]['value'].val

    def cloneCase(self,name,svnRemove=True,followSymlinks=False):
        out = SolutionDirectory.cloneCase(
                                    self,
                                    name,
                                    svnRemove=svnRemove,
                                    followSymlinks=followSymlinks
                                    )
        out.inletPatch = self.inletPatch
        out.updateInletVelocity()
        return out

    def createDataFile(self):
        runTimeObj = None

        for fI in listdir(self.name):
            if fI in ("forces", "forcesFS", "resistance"):
                runTimeObj = fI
        
        if not runTimeObj:
            return False
        else:
            path = join(
                        self.name,
                        runTimeObj,
                        listdir(join(self.name,runTimeObj))[0],
                        '%s.dat' %(runTimeObj)
                        )
            return DataFile.dataFile(path)
