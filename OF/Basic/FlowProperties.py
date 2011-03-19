from math import sqrt
from OF import Constants

def Re(**kwargs):
    """
    Calculates the Reynoldsnumber given by

    :math:`Re = \\frac{v*S_{wett}}{\\nu}`

    If the velocity is given, the Reynoldsnumber is returned and if a
    Froudenumber is provided as an argument, the Reynoldsnumber is calculated
    for the corresponding velocity. If the function gets a Reynoldsnumber as a
    parameter, the velocity is returned.
    
    :param v: Velocity
    :type v: float
    :param Re: Reynoldsnumber
    :type Re: float
    :param Fr: Froudenumber
    :type Fr: float
    :param L: Reference length
    :type L: float
    :param nu: Kinematic viscosity
    :type nu: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """
    try:
        nu = kwargs['nu']
    except KeyError:
        nu = Constants.water['nu']

    if 'v' in kwargs.iterkeys():
        return kwargs['v']*kwargs['L']/nu

    elif 'Fr' in kwargs.iterkeys():
        return Fr(
                    Fr=kwargs['Fr'],
                    L=kwargs['L']
                 )

    elif 'Re' in kwargs.iterkeys():
        return kwargs['Re']*nu/kwargs['L']


def Fr(**kwargs):
    """
    Calculates the Froudenumber given by

    :math:`Re = \\frac{v*}{\sqrt{gL}}`

    If the velocity is given, the Froudenumber is returned and if a
    Reynoldsnumber is provided as an argument, the Froudenumber is calculated
    for the corresponding velocity. If the function gets a Froudenumber as a
    parameter, the velocity is returned.
    
    :param v: Velocity
    :type v: float
    :param Re: Reynoldsnumber
    :type Re: float
    :param Fr: Froudenumber
    :type Fr: float
    :param L: Reference length
    :type L: float
    :param nu: Kinematic viscosity
    :type nu: float

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """
    if 'v' in kwargs.iterkeys():
        return kwargs['v']/sqrt(Constants.g*kwargs['L'])

    elif 'Re' in kwargs.iterkeys():
        vRe =  Re(
                    Re=kwargs['Re'],
                    L=kwargs['L']
                )
        return Fr(v=vRe,L=kwargs['L'])

    elif 'Fr' in kwargs.iterkeys():
        return kwargs['Fr']*sqrt(Constants.g*kwargs['L'])
