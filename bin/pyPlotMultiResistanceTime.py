#!/usr/bin/python 

"""
Can plot the resistance (viscous,total) and the respective coefficients
over the run time for multiple cases. The ITTC\'57 correlation line
can be included as well as a reference. All lines are named according to the
current case name and shown in the legend.
"""

import sys
import getopt
from optparse import OptionParser,OptionGroup
from os import path,getcwd,listdir
from re import compile,findall

import matplotlib.pyplot as plt 
import matplotlib as mpl
from numpy import abs,ones,mean,average

from OF import Settings
from OF.PostProcessing import DataFile
from OF.Basic import Case, Utilities, FlowProperties
from OF.NavalHydro import SkinFriction, Resistance

mpl.rc('lines', linewidth=2, color='r')

def main():
    parser = OptionParser(
                            usage="usage: %prog [options] area ref.Length",
                            version="%prog 1.0",
                            description=__doc__
                        )

    parser.add_option(
                    "-c", "--case",
                    action="append",
                    dest="cases",
                    type="string",
                    help="Specifies multiple cases and has to be called multiple\
                        times to do so."
                    )

    parser.add_option(
                    "-p", "--pattern",
                    action="store",
                    dest="pattern",
                    type="string",
                    help="Specifies the cases in the current working directory\
                        via regular expressions."
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
                    "-s", "--start",
                    action="store",
                    dest="startAtTime",
                    type="float",
                    default=0.0,
                    help="Starttime of the plotting interval, spanning from that\
                        time to the end. (default=0.0)"
                    )
    parser.add_option(
                    "-e", "--end",
                    action="store",
                    dest="endAtTime",
                    type="float",
                    default=1000000.0,
                    help="Endtime of the plotting interval"
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
                    "-d","--data",
                    action="store",
                    type="choice",
                    choices=['CF','CT','RF','RT'],
                    dest="dataToPlot",
                    default='CF',
                    help="Sets the data to be plotted. (default=CF)"
                    )

    group = OptionGroup(parser,"Flag Options")
    group.add_option(
                    "--without-ittc57",
                    action="store_true",
                    dest="withoutIttc",
                    help="Do not print ITTC\'57 correlation line"
                    )
    group.add_option(
                    "--without-average",
                    action="store_true",
                    dest="withoutAverage",
                    help="Do not calculate the average of the data"
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
    group.add_option(
                    "--ittc-start",
                    action="store",
                    dest="ittcStart",
                    type="float",
                    default=0.5,
                    help="Start of the averaging interval. (default=0.5)"
                    )
    group.add_option(
                    "--ittc-end",
                    action="store",
                    dest="ittcEnd",
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
    cases = []
    longestDataSet = -1
    i = 0
    CTaverage = []

    caseFolders = []
    if options.pattern:
        casePattern = compile(r"%s" %(options.pattern.replace(
                                                        "_F_",
                                                        Settings.floatPattern
                                                        )))
        for fI in listdir(getcwd()):
            if findall(casePattern,fI):
                caseFolders.append(fI)
    else:
        caseFolders = options.cases

    # Gather all cases
    for cI in caseFolders:
        cases.append(
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
        cases[-1].calculateCoeffs()



        # Figure out which data set is the longest
        if len(cases[i].t) >= len(cases[longestDataSet].t):
            longestDataSet = i
        i += 1

    # Store the length of all data sets in an extra list
    dataLengths = [len(cI.t) for cI in cases]


    # Initialise the plot
    fig = plt.figure(figsize=(11, 6))
    plt.title("Comparison of resistances")
    plt.grid(True)
    ax1 = fig.add_subplot(111)
    ax1.set_xlabel("simulation time [s]") 
    ax1.set_ylabel("CF [-]")

    # Shink current axis by 20%
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.7, box.height])

    plt.grid(True)

    allPlots = []
    # Create a list with all Reynoldsnumbers in it. This is needed for the
    # decision, whether only one or multiple ITTC lines have to be plotted
    Re = []
    ReNumbers = len(list(set([cI.Re for cI in cases])))
    for cI in cases:
        startAtElement = DataFile.element(
                                        cI.t,
                                        options.startAtTime,
                                        True
                                        )
        endAtElement = DataFile.element(
                                        cI.t,
                                        options.endAtTime,
                                        True
                                        )
        # The average of CF needs to be calculated anyway, as it is needed for
        # the ittc deviation calculation.
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
        ave = average(cI.resistances[options.dataToPlot][aveStart:aveEnd])
        if not options.withoutAverage:
            label = "%s (%.2e)" %(cI.shortCaseName,ave)
        else:
            label = cI.shortCaseName

        allPlots.append(
            ax1.plot(
                    cI.t[startAtElement:endAtElement],
                    cI.resistances[options.dataToPlot][startAtElement:endAtElement],
                    '-',
                    label=label
            )
        )
        
        # If the ITTC line is enabled, calculate the numpy array for each
        # dataset and fill the area between the respective CF curve and the ITTC
        # line with the same color. Then the relative deviation between CF and
        # ITTC is annotated.
        if not options.withoutIttc and options.dataToPlot == 'CF':
            ittcStart = DataFile.element(
                                        cI.t[startAtElement:endAtElement],
                                        options.ittcStart,
                                        options.withAbsolute
                                        )
            ittcEnd = DataFile.element(
                                        #cI.t,
                                        cI.t[startAtElement:endAtElement],
                                        options.ittcEnd,
                                        options.withAbsolute
                                        )
            ittc57 = ones(len(cI.t))*SkinFriction.ittc57(Re=cI.Re)
            ax1.fill_between(
                            cI.t[ittcStart:ittcEnd],
                            cI.resistances[options.dataToPlot][ittcStart:ittcEnd],
                            ittc57[ittcStart:ittcEnd],
                            color=allPlots[-1][0].get_color(),
                            alpha=0.5
                            )
            if not cI.Re in Re and ReNumbers > 1:
                label='ITTC\'57 (%.2e)' %(ittc57[0])
                allPlots.append(
                    ax1.plot(
                            cases[longestDataSet].t[startAtElement:endAtElement],
                            ittc57[startAtElement:endAtElement],
                            '--',
                            color=allPlots[-1][0].get_color(),
                            label=label
                    )
                )


            # Compute the deviation of the current CF from the ITTC line and
            # create a label inside the plot, that shows the relative deviation
            # as a numerical value.
            deviationList = cI.resistances[options.dataToPlot]*100.0/ittc57 - 100
            centerX = cI.t[int(ittcStart + (ittcEnd-ittcStart)/2)]
            centerY = min(ave,ittc57[0]) + (max(ave,ittc57[0])-min(ave,ittc57[0]))/2
            plt.text(
                centerX,
                centerY,
                '%.2f%%' %average(deviationList[ittcStart:ittcEnd])
                )
        # Finally append the current Reynoldsnumber to the global list of
        # Reynoldsnumbers.
        Re.append(cI.Re)



    if not options.withoutIttc and options.dataToPlot == 'CF':
        ittc57 = ones(dataLengths[longestDataSet])*\
                SkinFriction.ittc57(Re=cases[-1].Re)
        startAtElement = DataFile.element(
                            cases[longestDataSet].t,
                            options.startAtTime,
                            True
                        )
        endAtElement = DataFile.element(
                            cases[longestDataSet].t,
                            options.endAtTime,
                            True
                        )
        if not options.withoutIttc and ReNumbers == 1:
            label='ITTC\'57 (%.2e)' %(ittc57[0])
            allPlots.append(
                ax1.plot(
                        cases[longestDataSet].t[startAtElement:endAtElement],
                        ittc57[startAtElement:endAtElement],
                        '--',
                        color='black',
                        label=label
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

