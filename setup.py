from setuptools import setup
import os


datafiles = []
for root, dirs, files in os.walk("lasmerge/LAStools/"):
      for file in files:
            datafiles.append((root, [os.path.join(root, file)]))

setup(name='ply2las',
      version='1.0.0',
      packages=['ply2las', 'lasmerge'],
      include_package_data=True,
      url='https://github.com/terraref/ply2las',
      data_files = datafiles
      )
