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



"""
grmpf
"""

import sys
import getopt
from optparse import OptionParser,OptionGroup
from os import path,getcwd,listdir
from re import compile,findall

import matplotlib.pyplot as plt 
import matplotlib as mpl
from numpy import abs,mean,average,array,lexsort,linspace,std

from OF import Settings
from OF.PostProcessing import DataFile
from OF.Basic import Case, Utilities, FlowProperties
from OF.NavalHydro import SkinFriction, Resistance

mpl.rc('lines', linewidth=1, color='r')

def main():
    parser = OptionParser(
                            usage="usage: %prog [options] area ref.Length",
                            version="%prog 1.0",
                            description=__doc__
                        )

    parser.add_option(
                    "-s", "--data-set",
                    action="append",
                    dest="dataSets",
                    type="string",
                    help="Specifies a set of cases in the current working directory,\
                        that are considered to be of one data set. The selection is\
                        done via regular expressions. Multiple data sets can be\
                        specified."
                    )
    parser.add_option(
                    "-i", "--inlet",
                    action="store",
                    dest="inletPatch",
                    type="string",
                    default="XMAX",
                    help="Name of the inlet patch. (default=XMAX)"
                    )
    parser.add_option(
                    "-f",
                    action="store",
                    type="choice",
                    choices=['1','-1','2','-2','3','-3'],
                    dest="direction",
                    default=-1,
                    help="Main flow direction (1=x,2=y,3=z). (default=1)"
                    )
    parser.add_option(
                    "-x","--x-data",
                    action="store",
                    type="choice",
                    choices=['v','Fr','Re'],
                    dest="xDataToPlot",
                    default='Fr',
                    help="Which data to show on the x-axis. (default=Fr)"
                    )
    parser.add_option(
                    "-y","--y-data",
                    action="store",
                    type="choice",
                    choices=['CF','CT','RF','RT'],
                    dest="yDataToPlot",
                    default='CF',
                    help="Which data to show on the y-axis. (default=CF)"
                    )

    group = OptionGroup(parser,"Flag Options")
    group.add_option(
                    "--without-ittc57",
                    action="store_true",
                    dest="withoutIttc",
                    help="Do not print ITTC\'57 correlation line"
                    )
    group.add_option(
                    "--without-errorbars",
                    action="store_true",
                    dest="withoutErrorbars",
                    help="Do not print the error bars for the averaging"
                    )
    parser.add_option_group(group)

    group = OptionGroup(parser,"Statistics Options")
    group.add_option(
                    "--with-absolute",
                    action="store_true",
                    dest="withAbsolute",
                    help="If specified, all statistics intervalls have to be\
                        defined in terms of absolute times, rather than\
                        relatives"
                    )
    group.add_option(
                    "--average-start",
                    action="store",
                    dest="averageStart",
                    type="float",
                    default=0.5,
                    help="Start of the averaging interval. (default=0.5)"
                    )
    group.add_option(
                    "--average-end",
                    action="store",
                    dest="averageEnd",
                    type="float",
                    default=1.0,
                    help="End of the averaging interval. (default=1.0)"
                    )
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("wrong number of arguments")

    # Get the reference area and reference lengths from the command line
    # parameters. U needs to be evaluated, as either a string containg "False"
    # is passed or a string with a 3D list in it.
    area = float(args[0])
    L = float(args[1])

    ############################ 
    # Variable initialisations #
    ############################ 
    startAtElement = 0
    dataSets = []

    dataSetNames = []
    thisSet = []
    for sI in options.dataSets:
        setPattern = compile(r"%s" %(sI.replace("_F_",Settings.floatPattern)))

        for fI in listdir(getcwd()):
            if findall(setPattern,fI):
                thisSet.append(fI)
        dataSetNames.append(thisSet)
        thisSet = []

    # Gather all cases
    for sI in dataSetNames:
        casesOfThisSet = []
        for cI in sI:
            casesOfThisSet.append(
                    Case.case(
                            path.join(getcwd(),cI),
                            archive=None,
                            paraviewLink=False,
                            inletPatch=options.inletPatch,
                            L=L,
                            A=area,
                            direction=options.direction
                            )  
                    )
            # Calculation of force coefficients has to be called explicitely, as the
            # area and a reference length have to be specified. Furtheron it is not
            # essential that forces are present.
            casesOfThisSet[-1].calculateCoeffs()
        dataSets.append(casesOfThisSet)
        casesOfThisSet = []

    if options.xDataToPlot == 'v':
        unitX = 'm/s'
    else:
        unitX = '-'
    if options.yDataToPlot in ('RT','RF'):
        unitY = 'N'
    else:
        unitY = '-'

    # Initialise the plot
    fig = plt.figure(figsize=(11, 6))
    plt.title("Comparison of resistances over velocity")
    plt.grid(True)
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel("%s [%s]" %(options.xDataToPlot,unitX)) 
    ax1.set_ylabel("%s [%s]" %(options.yDataToPlot,unitY))

    # Shink current axis by 20%
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.7, box.height])

    plt.grid(True)

    allPlots = []
    dataToPlot = []
    thisSetToPlot = []
    Re = [1e15,0]
    Fr = [1e15,0]
    uInf = [1e15,0]
    for sI in dataSets:
        for cI in sI:
            aveStart = DataFile.element(
                                        cI.t,
                                        options.averageStart,
                                        options.withAbsolute
                                        )
            aveEnd = DataFile.element(
                                        cI.t,
                                        options.averageEnd,
                                        options.withAbsolute
                                        )
            ave = average(cI.resistances[options.yDataToPlot][aveStart:aveEnd])

            # Update velocities
            Re[0] = min(Re[0],cI.Re)
            Re[1] = max(Re[1],cI.Re)
            Fr[0] = min(Fr[0],cI.Fr)
            Fr[1] = max(Fr[1],cI.Fr)
            uInf[0] = min(uInf[0],cI.uInf)
            uInf[1] = max(uInf[1],cI.uInf)

            tmpList = [
                        cI.Fr,
                        cI.Re,
                        cI.uInf,
                        ave,
                        std(cI.resistances[options.yDataToPlot][aveStart:aveEnd])
                    ]
            thisSetToPlot.append(tmpList)

        dataToPlot.append(thisSetToPlot)
        thisSetToPlot = []
    dataToPlot = array(dataToPlot)

    i = 0
    for dI in dataToPlot:
        # The data needs to be sorted
        # http://stackoverflow.com/questions/2706605/sorting-a-2d-numpy-array-by-multiple-axes
        ind=lexsort((dI[:,1],dI[:,0]))    
        sorted = dI[ind]

        if options.xDataToPlot == 'v':
            xData = sorted[:,2]
        elif options.xDataToPlot == 'Fr':
            xData = sorted[:,0]
        else:
            xData = sorted[:,1]

        if not options.withoutErrorbars:
            allPlots.append(
                        ax1.errorbar(
                                xData,
                                sorted[:,3],
                                sorted[:,4],
                                fmt='-,',
                                )
                    )
        else:
            allPlots.append(
                        ax1.plot(
                                xData,
                                sorted[:,3],
                                '-o',
                                label=options.dataSets[i]
                        )
                    )
        i += 1

    if not options.withoutIttc:
        ittcRe = linspace(Re[0],Re[1],100)
        if options.xDataToPlot == 'Fr':
            xData = linspace(Fr[0],Fr[1],100)
        elif options.xDataToPlot == 'v':
            xData = linspace(uInf[0],uInf[1],100)
        else:
            xData = ittcRe
        ittc = SkinFriction.ittc57(Re=ittcRe)
        allPlots.append(
                    ax1.plot(
                            xData,
                            ittc,
                            '-',
                            color='black',
                            label='ITTC\'57'
                    )
                )


    # Assemble all plots for a proper legend
    lines = [pI[0] for pI in allPlots]
    labels = [l.get_label() for l in lines] 
    ax1.legend(
                lines,
                labels,
                bbox_to_anchor=(1.02, 1),
                loc=2,
                #mode="expand",
                #borderaxespad=0.,
                ncol=1
            )
    plt.show()

if __name__ == "__main__":
    main()

