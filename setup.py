#Copyright (C) 2013 Jens Hoepken

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


from distutils.core import setup

import glob,os

scriptlist = glob.glob('bin/*.py')


setup(name='OF',
      version='1.0',
      packages=[
                'OF',
                'OF.PostProcessing',
                'OF.NavalHydro',
                'OF.Basic',
                'OF.Mesh'
                ],
      description='Python library to simplify the usage of OpenFOAM',
      url='http://www.navitential.com',
      author='Jens Hoepken',
      author_email='jhoepken@gmail.com',
      scripts=scriptlist,
      )

