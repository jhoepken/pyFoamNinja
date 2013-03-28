#!/usr/bin/python
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



from os import getcwd,path,makedirs
from optparse import OptionParser,OptionGroup
import math
from numpy import linspace,array

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector

from OF.Basic import Case, Turbulence, Utilities

def main(argv=None):
    """
    """
    parser = OptionParser(
                            usage="usage: %prog [options]",
                            version="%prog ",
                            description=__doc__
                        )

    parser.add_option(
                    "-m",
                    action="store",
                    dest="mesh",
                    type="string",
                    default="",
                    help="Specifies the mesh to work on"
                    )

    parser.add_option(
                    "-t",
                    action="store",
                    dest="template",
                    type="string",
                    default="template",
                    help="""Specifies the template case, that will be cloned.
(Default = template)"""
                    )

    parser.add_option(
                    "-s", "--subpath",
                    action="store",
                    dest="subpath",
                    type="string",
                    default="",
                    help="""Optional subpath. This should be used to sort custom
parameter variations into the existing file structure.
%mesh/(%subpath, optional)/%beta/%v
"""
                    )

    parser.add_option(
                    "-b",
                    action="store",
                    dest="beta",
                    type="float",
                    default=0.0,
                    help="Drift angle beta (Default = 0.0)"
                    )

    parser.add_option(
                    "-n",
                    action="store",
                    dest="steps",
                    type="int",
                    default=10,
                    help="""Number of velocities between 0 and vMax. 
v=0 m/s will be neglected. (Default = 10)"""
                    )
    parser.add_option(
                    "-u",
                    action="store",
                    dest="u",
                    type="string",
                    default="0.0",
                    help="Service speed in m/s (Default = 0.0m/s)"
                    )
    parser.add_option(
                    "-r",
                    action="store",
                    dest="dh",
                    type="float",
                    default=100.0,
                    help="""Characteristic length of the flow. For ships this
should be the shiplength. (Default = 100.0m)"""
                    )

    group = OptionGroup(parser,"Flag Options")
    group.add_option(
                    "--without-turbulence",
                    action="store_true",
                    dest="withoutTurbulence",
                    help="""Do not look for the turbulence model and set the
particular values in the boundary conditions. The values are calculated based 
on the equations presented in the Fluent (R) handbook."""
                    )
    parser.add_option_group(group)


    (options, args) = parser.parse_args()

    try:
        u = float(options.u)
        v = linspace(0, u, options.steps + 1)[1:]
    except ValueError:
        exec "v =  array(%s)" %options.u

    # Assemble the current working directory
    workingDir = path.join(getcwd(),options.mesh)

    # Put together the name of the target angle folder
    driftAngleName = "beta%.2f" %options.beta

    # Assemble the absolute path of the angle folder
    if not options.subpath:
        driftAngleDirectory = path.join(workingDir,driftAngleName)
    else:
        driftAngleDirectory = path.join(workingDir,options.subpath,driftAngleName)

    # Check if the directory exists, that should store the cases for the current
    # drift angle.
    if not path.exists(driftAngleDirectory):
        makedirs(driftAngleDirectory)
    else:
        raise IOError("Directory %s does already exist" %driftAngleDirectory)


    template = Case.case(
                            path.join(getcwd(),options.mesh,options.template),
                            archive=None,
                            paraviewLink=False
                            )
    template.addToClone("runCluster")
    template.addToClone("customRegexp")

    print "\nDrift angle beta = %.2f\n" %options.beta

    i = 1
    for vI in v:
        print "Cloning case for v = %.3f" %vI

        # Clone the template case and open velocity boundary condition
        case = template.cloneCase(path.join(driftAngleDirectory,"v%02d" %i))
        uFile = ParsedParameterFile(path.join(case.name,"0","U"))

        # Rotate the velocity vector around z axis, according to the specified
        # drift angle.
        U = Vector(
                vI*math.cos(math.radians(options.beta)),
                vI*math.sin(math.radians(options.beta)),
                0
                )

        # Update the boundary condition(s) with the respective values, that have
        # been calculated previously.
        uFile["internalField"].setUniform(U)
        for b in ["XMIN","XMAX","YMIN","YMAX","ZMIN", "ZMAX"]:

            patchType = uFile["boundaryField"][b]['type']
            setPatch = False
            for inlet in ['value', 'inletValue', 'tangentialVelocity']:
                try:
                    uFile["boundaryField"][b][inlet].setUniform(U)
                    setPatch = True
                except KeyError:
                    pass

            if setPatch:
                print "\tSetting patch: %s type %s" %(b, patchType)

        # Write changes to the boundary conditions
        uFile.writeFile()

        if not options.withoutTurbulence:
            print "\tFixing turbulence Dh =", options.dh
            case.writeTurbulence(options.dh, Utilities.mag(U))
        
        # Update counter
        i += 1

    print "\nDone!"

if __name__ == "__main__":
    main()

