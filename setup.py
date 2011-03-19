from distutils.core import setup

import glob,os

scriptlist = glob.glob('')


setup(name='OF',
      version='1.0',
      packages=[
                'OF',
                'OF.PostProcessing',
                'OF.NavalHydro',
                'OF.Basic'
                ],
      description='Python library to simplify the usage of OpenFOAM',
      url='http://www.navitential.com',
      author='Jens Hoepken',
      author_email='jhoepken@gmail.com',
      scripts=scriptlist,
      )

