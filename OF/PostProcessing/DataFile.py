import numpy
import re

class dataFile():
    """
    Representation of a data file, that stores the data in a tabulated
    style, similar to the ``forces`` and ``forceCoeffs`` output.

    :Author: Jens Hoepken <jhoepken@gmail.com>
    :Author: Tomislav Maric <tomislav.maric@gmx.com>
    """

    _path = None
    """
    Path to the data file

    :type: string
    """

    _fileData = None
    """
    Content of the file, read via :meth:`readlines()`

    :type: list
    """

    def __init__(self, path):
        """
        :param path: Path to the data file
        :type path: string
        """

        self._path = path

        # Read the data file via readlines and store the content
        self._fileData = open(path,"r").readlines()
        self.parse()

    def __getitem__(self,key):
        # Get the column data from the _fileData array.
        return self._fileData[:,key]

    def parse(self):
        """
        Uses regular expressions to extract a list of numbers from the lines in
        the file. Skips all lines that start with a comment symbol.
        """
        parsedData = []

        # Regular expression for a number: integer, float, double with support
        # for scientific notation.
        numberRe = re.compile(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
        # Possible line comments.
        lineComments = ("//", "%","#") 

        for line in self._fileData:
            # Remove the whitespace on the left of the line.
            line = line.lstrip()
            if not line.startswith(lineComments):
                # re.findall returns a list of strings that are to be mapped
                # into float values by the "map" builtin function.
                # The result will be a list of numbers that are added to the
                # data list.
                parsedData.append(map(lambda number: float(number),
                    re.findall(numberRe,line)));

        # Overwrite the file raw ASCII data with the numpy.array object that
        # is a result of the data mining. 
        self._fileData = numpy.array(parsedData)

def element(times,target,absolute=False):
    """
    Finds and returns the array element number where the time is approximately
    equal to the target. If no such time is found, the id of the last element is
    returned.

    :param times: All time values
    :type times: numpy.array
    :param target: The time for which the element id has to be found. If
    relative is ``True``, it states the relative position inside the times.
    :type target: float

    :rtype: int
    """
    if not absolute:
        targetTime = target*times[-1]
    else:
        targetTime = target
    i = 0
    for tI in times:
        if tI >= targetTime:
            return i
        i += 1
    return i

