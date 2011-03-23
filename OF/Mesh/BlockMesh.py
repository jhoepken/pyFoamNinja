from os.path import join
import math

from PyFoam.Basics.DataStructures import Vector
from PyFoam.Basics.TemplateFile import TemplateFile
from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict

class blockMesh:

    def __init__(
                self,
                case,
                blocks,
                patches
                ):

        self.case = case
        self.blocks = blocks
        self.patches = patches


    def patchEntries(self):
        output = []
        for pI in self.patches:
            output.append("%s %s" %(pI.type,pI.name))
            output.append(pI.getFaces())

        return output


    def getVertices(self):
        output = []

        for vI in self.blocks[0].vertices[0].allVertices():
            output.append(vI)


        #for blockI in self.blocks:
            #for vI in blockI.vertices:
                #if not vI.duplicate and not vI in output:
                    #output.append(vI)
                    #vI.order = i
                    #
                    #for vJ in vI.allVertices():
                        #if vJ == vI:
                            #print vI
                            #vJ.order = i

                    #i += 1

        return output

    def getBlocks(self):
        
        output = []
        for blockI in self.blocks:
            v = " ".join([str(vI.order) for vI in blockI.vertices])
            print v
            output.append("hex (%s) (%i %i %i) simpleGrading (%f %f %f)" %(v,
                                                                blockI.nodes[0],
                                                                blockI.nodes[1],
                                                                blockI.nodes[2],
                                                                1,1,1))
        return output


    def write(self):
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
        template['vertices'] = self.getVertices() #[bI for blockI in self.blocks for bI in blockI.vertices]

        template['blocks'] = self.getBlocks()

        #template['patches'] = self.patchEntries()

        template.writeFile()

class patch:
    
    def __init__(
                self,
                name,
                faces,
                type = "patch"
                ):

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

    def __init__(
                self,
                vertices,
                nodes=False
                ):

        # Increase the global blockCount for the next block
        self.__class__.blockCount += 1

        self.id = self.__class__.blockCount 
        """
        Stores the id of the current block, which is basically nothing else than
        a global counter for all existing blocks.

        :type: int
        """

        self.nodes = nodes

        self.faces = []


        # Create from 8 vertices
        if isinstance(vertices,list) and len(vertices) == 8:
            print "Constructing block from 8 vertices"
            self.vertices = vertices

        # Create from bounding box
        elif isinstance(vertices,list) and len(vertices) == 2:
            print "Constructing block from 2 vertices"
            self.vertices = boundingBox(vertices[0],vertices[1])

        else:
            raise ValueError("Incorrect numbers of vertices passed to create a block")
            
            
        from pprint import pprint
        print "Vertices in Block:"
        pprint(self.vertices)

        self.generateFaces()


    def generateFaces(self):
        # xmin face
        self.faces.append(face([
                                self.vertices[4],
                                self.vertices[7],
                                self.vertices[3],
                                self.vertices[0]
                                ]))

        # xmax face
        self.faces.append(face([
                                self.vertices[6],
                                self.vertices[5],
                                self.vertices[1],
                                self.vertices[2]
                                ]))

        # ymin face
        self.faces.append(face([
                                self.vertices[5],
                                self.vertices[4],
                                self.vertices[0],
                                self.vertices[1]
                                ]))

        # ymax face
        self.faces.append(face([
                                self.vertices[7],
                                self.vertices[6],
                                self.vertices[2],
                                self.vertices[3]
                                ]))

        # zmin face
        self.faces.append(face([
                                self.vertices[3],
                                self.vertices[2],
                                self.vertices[1],
                                self.vertices[0]
                                ]))

        # zmax face
        self.faces.append(face([
                                self.vertices[4],
                                self.vertices[5],
                                self.vertices[6],
                                self.vertices[7]
                                ]))

    def getBlock(self):
        
        v = " ".join([str(vI.id) for vI in self.vertices])
        print v
        return "hex (%s) (%i %i %i) simpleGrading (%f %f %f)" %(v,
                                                                self.nodes[0],
                                                                self.nodes[1],
                                                                self.nodes[2],
                                                                1,1,1)

class face:

    def __init__(self,vertices):
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



def boundingBox(minV,maxV):
    """
    Creates all vertices for a bounding box and returns them as a list

    :param min: Minimum boundary
    :type min: :class:`~Mesher.BlockMesh.vertex`
    :param max: Maximum boundary
    :type max: :class:`~Mesher.BlockMesh.vertex`

    :rtype: list
    """
    return [
            minV,
            vertex(maxV[0],minV[1],minV[2]),
            vertex(maxV[0],maxV[1],minV[2]),
            vertex(minV[0],maxV[1],minV[2]),

            vertex(minV[0],minV[1],maxV[2]),
            vertex(maxV[0],minV[1],maxV[2]),
            maxV,
            vertex(minV[0],maxV[1],maxV[2])
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

    list = []
    """
    Global list, where all existing vertices are stored in.

    :type: list
    """

    def __init__(self, x, y, z): 
        """
        :param x: x coordinate
        :type x: float
        :param y: y coordinate
        :type y: float
        :param z: z coordinate
        :type z: float
        """
        # Ensure floats for the coordinates
        x = float(x)
        y = float(y)
        z = float(z)

        self.order = -1
        """
        Stores the order of this vertex in the output for blockMesh.

        :type: int
        """
        
        self.duplicate = False
        """
        Indicates whether a vertex at these coordinates does already exist or
        not.

        :type: bool
        """

        # Construct parent vector class
        Vector.__init__(self,x,y,z)

        # Register the coordinates
        self.x = x
        self.y = y
        self.z = z

        # If no vertex at the specified coordinates exist, it gets constructed,
        # the global counter is increased accordingly and the id is assigned.
        # The vertex is appended to the global vertex list
        if not self.exists(x,y,z):
            self.id = self.__class__.vertexCount + 1
            self.__class__.vertexCount += 1
            self.duplicate = False

        # If the vertex does exist, clone it and set the duplicate to True
        else:
            self = self.exists(x,y,z)
            self.duplicate = True
            print "Vertex does already exist. ", self.order

        self.__class__.list.append(self)
        self.ensureOrder()
            

    def ensureOrder(self):
        i = 0

        for vI in self.list:
            exists = False
            for vJ in self.list:
                if vI == vJ and vI.id != vJ.id and vI.duplicate:
                    vI.order = vJ.order
                    exists = True
                else:
                    vI.order = i
            if not exists:
                i += 1


    def __repr__(self):
        return "%i,%i\t(%f %f %f)" %(self.id,self.order,self.x,self.y,self.z)

    def __eq__(self,other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        else:
            return False

    def allVertices(self):
        return self.__class__.list

    def exists(self,x,y,z):
        for lI in self.__class__.list:
            if (lI.x == x) and (lI.y == y) and (lI.z == z):
                return lI
        return False
