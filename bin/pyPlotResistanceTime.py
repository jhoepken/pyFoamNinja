#!/usr/bin/python 

import sys
import getopt
from optparse import OptionParser
from os import path,getcwd,listdir

import matplotlib.pyplot as plt 
import matplotlib as mpl
from numpy import abs,ones,mean

from OF.PostProcessing import DataFile
from OF.Basic import Case, Utilities, FlowProperties
from OF.NavalHydro import SkinFriction, Resistance

mpl.rc('lines', linewidth=2, color='r')

def main():
    parser = OptionParser(usage="usage: %prog [options] area ref.Length (case)",
                            version="%prog 1.0")

    parser.add_option(
                    "-U", "--velocity",
                    action="store",
                    dest="U",
                    type="string",
                    default="False",
                    help="Velocity vector as a list \"[x,y,z]\". If nothing is\
                        stated, a inlet patch needs to be specified. From that\
                        patch, the velocity is read automatically."
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
                    "-d", "--deviation-start",
                    action="store",
                    dest="deviationInterval",
                    type="float",
                    default=0.5,
                    help="Specifies over which part of the plotted interval, the\
                        relative deviation between CF and ITTC\'57 as well as\
                        the average of CF should be calculated. (default=0.5)"
                    )
    parser.add_option(
                    "-f",
                    action="store",
                    type="choice",
                    choices=['1','2','3'],
                    dest="direction",
                    default=1,
                    help="Main flow direction (1=x,2=y,3=z). (default=1)"
                    )

    (options, args) = parser.parse_args()

    if len(args) == 2:
        caseDir = getcwd()
    elif len(args) == 3:
        caseDir = args[2]
    else:
        parser.error("wrong number of arguments")

    area = float(args[0])
    L = float(args[1])
    U = eval(options.U)

    startAtElement = 0
    deviationStartElement = 0

    case = Case.case(
                    caseDir,
                    archive=None,
                    paraviewLink=False,
                    inletPatch=options.inletPatch,
                    U=U
                    )  

    uInf = Utilities.mag(case.inletVelocity)
    Re = FlowProperties.Re(L=L,u=uInf)
    
    data = case.forces

    t = data[0]
    RF = abs(data[options.direction+3])
    RT = RF + abs(data[options.direction])

    # The list element of the time has to be figured out, beyond which the
    # plotting should start.
    if options.startAtTime > 0.0:
        for i in range(0,len(data[0])):
            if data[0][i] > options.startAtTime:
                startAtElement = i
                break

    # Determine the start element for the deviation calculation
    deviationStartElement = startAtElement + \
            int(len(t[startAtElement:])*(1-options.deviationInterval))

    # Gather all data
    CF = Resistance.forceCoeff(RF,area,u=uInf)
    CT = Resistance.forceCoeff(RT,area,u=uInf)
    ittc57 = ones(len(CT))* SkinFriction.ittc57(Re=Re)
    deviationList = CF*100.0/ittc57 - 100

    # Calculate the relative error between CF and ITTC57 for the respective
    # intervall
    deviation = sum(deviationList[deviationStartElement:]) / \
                len(deviationList[deviationStartElement:])

    # Calculate mean value of CF for the respective interval
    CFmean = mean(CF[deviationStartElement:])
        

    fig = plt.figure()

    plt.title("case: %s\nCFmean = %.2e, rel.Error = %.2f%%, Re = %.2e"
              %(case.shortCasePath,CFmean,deviation,Re))
    plt.grid(True)
    ax1 = fig.add_subplot(111)
    plt.grid(True)
    ax2 = ax1.twinx() 
    CFPlot = ax1.plot(t[startAtElement:],CF[startAtElement:],'-',label='C_F',color='green') 
    ittc57Plot = ax1.plot(t[startAtElement:],
                          ittc57[startAtElement:],'-',label='ITTC57',color='red') 

    CTPlot = ax2.plot(t[startAtElement:],CT[startAtElement:],'-',label='C_T') 

    ax1.fill_between(t[deviationStartElement:],
                     CF[deviationStartElement:],
                     ittc57[deviationStartElement:],
                     color="green",alpha=0.5)

    ax1.set_xlabel("simulation time [s]") 
    ax1.set_ylabel("CF [-]")
    ax2.set_ylabel("CT [-]")
    #ax1.set_ylim([
    #            0,
    #            1.2*max(CF[startAtElement].max(),ittc57[0])
    #            ])

    lines = CFPlot+ittc57Plot+CTPlot
    labels = [l.get_label() for l in lines] 
    plt.legend(
                lines,
                labels,
                loc=9,
                #bbox_to_anchor=(0., 1.02, 1., .102),
                ncol=3,
                mode="expand"
            )
    plt.show()

if __name__ == "__main__":
    main()

