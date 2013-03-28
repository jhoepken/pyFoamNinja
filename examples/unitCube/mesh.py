#!/usr/bin/env python
from os import getcwd
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from Mesher import BlockMesh as BM

# Generate a PyFoam SolutionDirectory for easy access to the case data
case = SolutionDirectory(getcwd(), archive=None, paraviewLink=False)

# Width of the unit cube
width = 1.0

# Number of cells in each direction of the cube
cells = 10

# The first step is to generate the vertices for each block. Luckily the
# boundingBox method creates 8 vertices out of a min and max point, which
# saves us some typing. The block is aligned with its centre point in 
# the origin of the coordinate system.
points0 = BM.boundingBox(
            (-0.5*width,-0.5*width,-0.5*width),
            (0.5*width,0.5*width,0.5*width)
        )

# After the point definition, the blocks must get genrated from the points.
# We can pass a point list, cells/nodes+1 in all three directions as well as
# the respective edge grading to the constructor of a block.
block0 = BM.block(points0, nodes=[cells, cells, cells], gradings=[1,1,1])

# Though it makes no real sense for this example, we can generate patches from
# the boundary faces of a block, just as known from blockMesh itself. The patch
# class takes a name and a list of faces as required arguments and the type can
# be passed as an optional argument.
outside = BM.patch("OUTSIDE", [block0.faces[i] for i in range(0,6)])

mesh = BM.blockMesh(case)
mesh.addBlocks([block0])
mesh.addPatches([outside])
mesh.write() 
