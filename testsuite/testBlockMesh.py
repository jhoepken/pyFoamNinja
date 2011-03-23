from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.Basics.DataStructures import Vector
from OF.Mesh import BlockMesh 


case = SolutionDirectory("/home/jens/OpenFOAM/jens-1.6-ext/applications/iMesher/testCase", archive=None, paraviewLink=False)

a = [
    BlockMesh.vertex(0,0,0),
    BlockMesh.vertex(1,0,0),
    BlockMesh.vertex(1,1,0),
    BlockMesh.vertex(0,1,0),
    BlockMesh.vertex(0,0,1),
    BlockMesh.vertex(1,0,1),
    BlockMesh.vertex(1,1,1),
    BlockMesh.vertex(0,1,1)
]

b = [
    a[4],
    BlockMesh.vertex(1,1,5.32213)
]

c = [
    a[1],
    BlockMesh.vertex(3,1,1)
]

block1 = BlockMesh.block(a,[2,10,20])
block2 = BlockMesh.block(b,[2,10,20])
block3 = BlockMesh.block(c,[2,10,20])

from pprint import pprint
pprint(a[0].list)
print "///"
for vI in a[0].allVertices():
    print vI.order,vI
print "///"


#inlet = patch("INLET",[block1.faces[0]])
#print inlet

mesh = BlockMesh.blockMesh(case,[block1,block2,block3],[])
mesh.write()



#grmpf = ParsedBlockMeshDict("/home/hoepken/OpenFOAM/OpenFOAM-1.6-ext/tutorials/incompressible/simpleFoam/pitzDaily/constant/polyMesh/blockMeshDict")
#print grmpf['patches']
