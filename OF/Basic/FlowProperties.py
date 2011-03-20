from math import sqrt
from OF import Constants

"""
This package contains some descriptive flow parameters, that are used regularly.
"""

def Re(**kwargs):
    """
    Calculates the Reynoldsnumber given by

    ..math::
        
        Re = \\frac{v*L}{\\nu}


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
        return Fr(**kwargs)

    elif 'Re' in kwargs.iterkeys():
        return kwargs['Re']*nu/kwargs['L']


def Fr(**kwargs):
    """
    Calculates the Froudenumber given by

    ..math::

        Re = \\frac{v}{\sqrt{gL}}

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
        kwargs['v'] =  Re(**kwargs)
        return Fr(**kwargs)

    elif 'Fr' in kwargs.iterkeys():
        return kwargs['Fr']*sqrt(Constants.g*kwargs['L'])

def vFrRe(**kwargs):
    """
    Calculates the velocity, Reynoldsnumber and Froudenumber, based on one
    velocity description and a reference length. All three are returned.

    :rtype: float,float,float
    """
    velocityParams = ['v','Re','Fr']

    pCount = 0
    for vI in velocityParams:
        if vI in kwargs.iterkeys():
            pCount += 1
    

    if not kwargs['v'] and not kwargs['Re'] and not kwargs['Fr']:
        raise ValueError("Neither v nor Re and Fr have been provided")
    elif pCount > 1 :
        raise ValueError("Too many velocity definitions (Re, v, Fr)")

    if not 'L' in kwargs.iterkeys():
        raise ValueError("A reference length has to be specified")

    if kwargs['v']:
        v_ = kwargs['v']
        Fr_ = Fr(**kwargs)
        Re_ = Re(**kwargs)

    elif kwargs['Fr']:
        v_ = Fr(**kwargs)
        Fr_ = kwargs['Fr']
        Re_ = Re(**kwargs)

    elif kwargs['Re']:
        v_ = Re(**kwargs)
        Fr_ = Fr(**kwargs)
        Re_ = kwargs['Re']

    return v_,Fr_,Re_
