from OF import Constants

def Re(v,
        Swett,
        nu = Constants.nuWater):
    return v*Swett/nu
