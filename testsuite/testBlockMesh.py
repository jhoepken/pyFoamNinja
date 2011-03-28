from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.Basics.DataStructures import Vector
from OF.Mesh import BlockMesh 


case = SolutionDirectory("/Users/jens/OpenFOAM/jens-1.6/applications/iMesher/testCase", archive=None, paraviewLink=False)

points1 = [(0,0,0),(1,1,1)]
block1 = BlockMesh.block(points1,nodes=[2,10,20],gradings=[1,1,1])

points2 = [(1,0,0),(2,1,1)]
block2 = BlockMesh.block(points2,nodes={0:9},gradings={0:1})

points3 = [(0,1,0),(1,5,1)]
block3 = BlockMesh.block(points3,nodes={1:3},gradings={1:3})

points4 = [(0,1,-3),(1,5,0)]
block4 = BlockMesh.block(points4,nodes={2:15},gradings={2:0.5})

points5 = [(2,0,0),(5,1,1)]
block5 = BlockMesh.block(points5,nodes={0:4},gradings={0:1})

inlet = BlockMesh.patch("inlet",[
                                block1.faces[0],
                                block3.faces[0]
                                ])
top = BlockMesh.patch("top",[
                            block1.faces[5],
                            block2.faces[5],
                            block3.faces[5]
                            ],type="wall")


mesh = BlockMesh.blockMesh(case)
mesh.addBlocks([block1,block2,block3,block4,block5])
mesh.addPatches([inlet,top])
mesh.write()

from pprint import pprint
pprint(block1.gradings)
pprint(block2.gradings)
pprint(block3.gradings)
