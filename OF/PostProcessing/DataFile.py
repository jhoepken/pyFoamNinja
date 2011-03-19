import numpy

class dataFile():
    """
    Representation of a data file, that stores the data in a tabulated
    style, similar to the ``forces`` and ``forceCoeffs`` output.

    :Author: Jens Hoepken <jhoepken@gmail.com>
    """

    path = None
    """
    Path to the data file

    :type: string
    """

    file = None
    """
    Content of the file, read via :meth:`readlines()`

    :type: list
    """

    def __init__(self, path):
        """
        :param path: Path to the data file
        :type path: string
        """

        self.path = path

        # Read the data file via readlines and store the content
        tmpFile = open(path,"r")
        self.file = tmpFile.readlines()
        tmpFile.close()
        del tmpFile

        self.parse()

    def __getitem__(self,key):
        return numpy.array(self.file[key])

    def parse(self):
        """
        Strips all tabs, linebreaks and round brackets from the content and
        rearranges it as a nested list. Each entry of the list represents a
        column of the data file. If any line contains a sharp sign, the
        line is skipped.
        """

        data = False

        blackList = [
                        ")",
                        "(",
                        "\n",
                        "\t"
                    ]

        lineCounter = 0
        for line in self.file:
            if not "#" in line: #lineCounter > 0:
                
                for bI in blackList:
                    line = line.replace(bI,"")

                columns = line.split(" ")

                if not data:
                    data = columns
                    i = 0
                    while i < len(data):
                        data[i] = [float(data[i])]
                        i += 1

                else:
                    i = 0
                    for cI in columns:
                        data[i].append(float(cI))
                        i += 1

            lineCounter += 1

        self.file = data
