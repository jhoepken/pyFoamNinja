from os.path import join
from copy import deepcopy
import math

from PyFoam.Basics.DataStructures import Vector
from PyFoam.Basics.TemplateFile import TemplateFile
from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict

class blockMesh:

    def __init__(
                self,
                case
                ):

        self.case = case

        self.blocks = []

        self.vertices = []

        self.patches = []


    def patchEntries(self):
        """
        Returns the entries for the patches in the ``blockMeshDict``.

        :rtype: list
        """
        output = []
        for pI in self.patches:
            output.append("%s %s" %(pI.type,pI.name))
            output.append(pI.getFaces())
        return output

    def addPatches(self,patches):
        """
        Adds a patch to the mesh
        """
        self.patches += patches

    def addBlocks(self,blocks):
        """
        Adds blocks to the mesh. 
        """
        self.blocks += blocks
        self.vertices = blocks[0].vertices

    def check(self):
        for bI in self.blocks:
            print bI.neighbours
            bI.checkNodes()

    def getVertices(self):
        """
        Returns all vertices, but filters the ones which are only a reference.

        :rtype: list
        """
        output = []

        for vI in self.vertices:
            if not vI.duplicate:
                output.append(vI)

        return output

    def getBlocks(self):
        
        output = []
        for blockI in self.blocks:
            blockVertices = []
            for vI in blockI.ownVertices:
                try:
                    blockVertices.append(str(vI.id))
                except AttributeError:
                    blockVertices.append(str(vI))
            v = " ".join(blockVertices)
            print v
            output.append("hex (%s) (%i %i %i) simpleGrading (%f %f %f)" %(v,
                                                                blockI.nodes[0],
                                                                blockI.nodes[1],
                                                                blockI.nodes[2],
                                                                1,1,1))
        return output


    def write(self):
        self.check()

        target = join(self.case.polyMeshDir(),"blockMeshDict")

        template = TemplateFile(content="""
FoamFile
{
	version     2.0;
	format      ascii;
	class       dictionary;
	object      blockMeshDict;
}
convertToMeters    1.0;
vertices
(
);
blocks
(
);

patches
(
);
edges
();
// ************************************************************************* //
""")

        template.writeToFile(target,{})
        template = ParsedBlockMeshDict(
                                        join(
                                            self.case.polyMeshDir(),
                                            'blockMeshDict'
                                            )
                                        )
        # Adopted from
        # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        #template['vertices'] = self.getVertices() #[bI for blockI in self.blocks for bI in blockI.vertices]
        template['vertices'] = self.getVertices()

        template['blocks'] = self.getBlocks()

        template['patches'] = self.patchEntries()

        template.writeFile()

class patch:
    """
    Representation of a blockMesh patch. Each patch consists one or multiple
    faces.
    """
    
    def __init__(
                self,
                name,
                faces,
                type = "patch"
                ):
        """
        :param name: Name of the patch
        :type name: string
        :param faces: Faces the patch consists of
        :type faces: list
        :param type: Type of the patch (Default = ``patch``)
        :type type: string
        """

        self.name = name
        self.type = type

        self.faces = faces


    def __repr__(self):

        output = "%s %s" %(self.type,self.name)
        for fI in self.faces:
            output += "\n\t%s" %(fI.outputString())
        return output

    def getFaces(self):
        """
        Returns a list of the face ids for the current patch.

        :rtype: list
        """
        return [fI.verticeIds for fI in self.faces]


class block:

    blockCount = -1
    """
    Global counter for all generated blocks

    :type: int
    """

    vertices = []
    """
    Stores all existing vertices.

    :type: list
    """

    list = []
    """
    Stores all existing blocks.

    :type: list
    """

    edges = []
    """
    Stores all existing edges.

    :type: list
    """

    def __init__(
                self,
                points,
                nodes=False
                ):

        # Increase the global blockCount for the next block
        self.__class__.blockCount += 1

        self.__class__.list.append(self)

        self.id = self.__class__.blockCount 
        """
        Stores the id of the current block, which is basically nothing else than
        a global counter for all existing blocks.

        :type: int
        """

        self.ownVertices = []
        """
        Stores the vertices, that are used by the block

        :type: list
        """

        self.nodes = nodes

        self.faces = []
        """
        Stores the faces of the block.

        :type: list
        """

        self.ownEdges = []

        self.neighbours = {
                            0: False,
                            1: False,
                            2: False,
                            3: False,
                            4: False,
                            5: False
                            }
        """
        Stores the ids of the neighbouring blocks.

        :type: dict
        """


        # Create from 8 points
        if isinstance(points,list) and len(points) == 8:
            print "Constructing block from 8 points"
            for pI in points:
                self.checkDuplicateVertices(pI)


        # Create from bounding box
        elif isinstance(points,list) and len(points) == 2:
            print "Constructing block from 2 points"
            for pI in boundingBox(points[0],points[1]):
                self.checkDuplicateVertices(pI)

        else:
            raise ValueError("Incorrect numbers of points passed to create a block")
            
        self.generateFaces()
        self.generateEdges()
        self.findNeighbour()

    def __eq__(self,other):
        if self.id == other.id:
            return True
        else:
            return False

    def checkNodes(self):
        for dir,bNeighbourId in self.neighbours.iteritems():
            if not isinstance(bNeighbourId,bool):
                if dir == 0 or dir == 1:
                    if self.list[bNeighbourId].nodes[1] != self.nodes[1] or \
                       self.list[bNeighbourId].nodes[2] != self.nodes[2]:
                        raise ValueError("Nodes on edge mismatch")
                elif dir == 2 or dir == 3:
                    if self.list[bNeighbourId].nodes[0] != self.nodes[0] or \
                       self.list[bNeighbourId].nodes[2] != self.nodes[2]:
                        raise ValueError("Nodes on edge mismatch")
                elif dir == 4 or dir == 5:
                    if self.list[bNeighbourId].nodes[0] != self.nodes[0] or \
                       self.list[bNeighbourId].nodes[1] != self.nodes[1]:
                        raise ValueError("Nodes on edge mismatch")


    def ownToNeighbourId(self,id):
        """
        Translates the face id (0-5) from the current block, to the notation of
        the adjoining block and returns that id.

        :param id: Number of the block's face
        :type id: int

        :rtype: int
        """
        out = -1
        if id%2:
            return id - 1
        else:
            return id + 1


    def findNeighbour(self):
        """
        Finds the neighbouring blocks for the current block and stores their ids
        in :meth:`neighbours`. The search is pretty stupid and there is severe
        room for improvements.
        """

        # Check all existing blocks, but not self
        for bI in self.list:
            if bI != self:

                # Loop over all faces of the respective block and check if the
                # current block shares the same face. If so, exchange the
                # neighboring ids.
                for fI in bI.faces:
                    ownFace = 0
                    for fIOwn in self.faces:
                        if fI == fIOwn:
                            self.neighbours[ownFace] = bI.id
                            bI.neighbours[self.ownToNeighbourId(ownFace)] = self.id

                        ownFace += 1


    def checkDuplicateVertices(self,v):
        """
        Checks if certain coordinates v already exist as a vertex. If so,
        particular vertex is duplicated and the the duplicate property is set to
        ``True``. This duplicate is appended to the global and local vertex 
        list for later reference. Otherwise a new vertex is generated and 
        appended to both lists as well. If the coordinates do exist, the function
        returns ``True`` otherwise ``False``.

        :param v: Coordinates to be checked and added
        :type v: tuple

        :rtype: bool
        """
        for vI in self.vertices:
            if vI == v:
                vTemp = deepcopy(vI)
                vTemp.duplicate = True

                self.vertices.append(vTemp)
                self.ownVertices.append(vTemp)
                return True

        vTemp = vertex(v)
        self.vertices.append(vTemp)
        self.ownVertices.append(vTemp)
        return False


    def generateFaces(self):
        # xmin face
        self.faces.append(face([
                                self.ownVertices[4],
                                self.ownVertices[7],
                                self.ownVertices[3],
                                self.ownVertices[0]
                                ]))

        # xmax face
        self.faces.append(face([
                                self.ownVertices[6],
                                self.ownVertices[5],
                                self.ownVertices[1],
                                self.ownVertices[2]
                                ]))

        # ymin face
        self.faces.append(face([
                                self.ownVertices[5],
                                self.ownVertices[4],
                                self.ownVertices[0],
                                self.ownVertices[1]
                                ]))

        # ymax face
        self.faces.append(face([
                                self.ownVertices[7],
                                self.ownVertices[6],
                                self.ownVertices[2],
                                self.ownVertices[3]
                                ]))

        # zmin face
        self.faces.append(face([
                                self.ownVertices[3],
                                self.ownVertices[2],
                                self.ownVertices[1],
                                self.ownVertices[0]
                                ]))

        # zmax face
        self.faces.append(face([
                                self.ownVertices[4],
                                self.ownVertices[5],
                                self.ownVertices[6],
                                self.ownVertices[7]
                                ]))

    def generateEdges(self):
        # Edge 0
        self.edges.append(edge(
                                self.ownVertices[0],
                                self.ownVertices[1]
                            ))
                                
        # Edge 1
        self.edges.append(edge(
                                self.ownVertices[3],
                                self.ownVertices[2]
                            ))
                                
        # Edge 2
        self.edges.append(edge(
                                self.ownVertices[7],
                                self.ownVertices[6]
                            ))
                                
        # Edge 3
        self.edges.append(edge(
                                self.ownVertices[4],
                                self.ownVertices[5]
                            ))
                                
        # Edge 4
        self.edges.append(edge(
                                self.ownVertices[0],
                                self.ownVertices[3]
                            ))
                                
        # Edge 5
        self.edges.append(edge(
                                self.ownVertices[1],
                                self.ownVertices[2]
                            ))
                                
        # Edge 6
        self.edges.append(edge(
                                self.ownVertices[5],
                                self.ownVertices[6]
                            ))
                                
        # Edge 7
        self.edges.append(edge(
                                self.ownVertices[4],
                                self.ownVertices[7]
                            ))
                                
        # Edge 8
        self.edges.append(edge(
                                self.ownVertices[0],
                                self.ownVertices[4]
                            ))
                                
        # Edge 9
        self.edges.append(edge(
                                self.ownVertices[1],
                                self.ownVertices[5]
                            ))
                                
        # Edge 10
        self.edges.append(edge(
                                self.ownVertices[2],
                                self.ownVertices[6]
                            ))

        # Edge 11
        self.edges.append(edge(
                                self.ownVertices[3],
                                self.ownVertices[7]
                            ))

    def getBlock(self):
        
        v = " ".join([str(vI.id) for vI in self.vertices])
        print v
        return "hex (%s) (%i %i %i) simpleGrading (%f %f %f)" %(v,
                                                                self.nodes[0],
                                                                self.nodes[1],
                                                                self.nodes[2],
                                                                1,1,1)


class edge:

    edgeCount = 0

    def __init__(
                self,
                start,
                end,
                type='line',
                *args
                ):
        self.id = self.__class__.edgeCount
        self.__class__.edgeCount += 1

        self.start = start
        self.end = end
        self.type = type



class face:
    """
    Represents a face of a block, not a patch.
    """

    def __init__(self,vertices):
        """
        :param vertices: Vertices the face consists of
        :type vertices: list
        """
        self.vertices = vertices

        self.boundaryFace = True

        self.verticeIds = [vI.id for vI in self.vertices]

    def outputString(self):
        return "(%i %i %i %i)" %(self.vertices[0].id,
                                self.vertices[1].id,
                                self.vertices[2].id,
                                self.vertices[3].id)

    def __repr__(self):
        return self.outputString()

    def __eq__(self,other):
        if [True for vI in self.vertices if vI.id in other.verticeIds].count(True) == 4:
            return True
        else:
            return False


def boundingBox(minV,maxV):
    """
    Creates all vertices for a bounding box and returns them as a list

    :param min: Minimum boundary point
    :type min: tuple
    :param max: Maximum boundary point
    :type max: tuple

    :rtype: list
    """
    return [
            ((minV[0],minV[1],minV[2])),
            ((maxV[0],minV[1],minV[2])),
            ((maxV[0],maxV[1],minV[2])),
            ((minV[0],maxV[1],minV[2])),

            ((minV[0],minV[1],maxV[2])),
            ((maxV[0],minV[1],maxV[2])),
            ((maxV[0],maxV[1],maxV[2])),
            ((minV[0],maxV[1],maxV[2]))
            ]


class vertex(Vector):
    """
    Representation of a vertex, inherits
    :class:`PyFoam.Basics.DataStructures.Vector`, all each instance of itself in
    an internal list. By doing that, no extra class for the vertex list handling
    must be implemented and duplicate vertices can be handled in a fairly
    straight forward manner.
    """

    vertexCount = -1
    """
    Global counter for all existing vertices

    :type: int
    """

    id = 0
    """
    Id of the vertex

    :type: int
    """

    def __init__(self, p):
        """
        :param x: x coordinate
        :type x: float
        :param y: y coordinate
        :type y: float
        :param z: z coordinate
        :type z: float
        """
        # Ensure floats for the coordinates
        x = float(p[0])
        y = float(p[1])
        z = float(p[2])

        # Construct parent vector class
        Vector.__init__(self,x,y,z)

        # Register the coordinates
        self.x = x
        self.y = y
        self.z = z

        self.duplicate = False

        self.id = self.__class__.vertexCount + 1
        self.__class__.vertexCount += 1

            

    def __repr__(self):
        return "%i\t(%f %f %f)" %(self.id,self.x,self.y,self.z)

    def __eq__(self,other):
        if isinstance(other,tuple):
            if self.x == other[0] and self.y == other[1] and self.z == other[2]:
                return True
        else:
            if self.x == other.x and self.y == other.y and self.z == other.z:
                return True
        return False

