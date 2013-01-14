from math import sqrt

def mag(v):
    """
    Calculates and returns the magnitude of a vector

    :param v: Vector of which the magnitude should be determinded
    :type v: tuple/list
    :rtype: float
    """
    return sqrt(v[0]**2+v[1]**2+v[2]**2)
