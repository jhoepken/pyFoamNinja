from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.Basics.DataStructures import Vector
from OF.Mesh import BlockMesh 


case = SolutionDirectory("/Users/jens/OpenFOAM/jens-1.6/applications/iMesher/testCase", archive=None, paraviewLink=False)

points1 = [(0,0,0),(1,1,1)]
block1 = BlockMesh.block(points1,[2,10,20])

points2 = [(1,0,0),(2,1,1)]
block2 = BlockMesh.block(points2,[2,10,20])

points3 = [(0,1,0),(1,5,1)]
block3 = BlockMesh.block(points3,[2,10,20])

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
mesh.addBlocks([block1,block2,block3])
mesh.addPatches([inlet,top])
mesh.write()

