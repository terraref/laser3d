from setuptools import find_packages, setup
import os


datafiles = []
for root, dirs, files in os.walk("terraref/laser3d/LAStools/"):
      for file in files:
            datafiles.append((root, [os.path.join(root, file)]))

setup(name='terraref-laser3d',
      version='1.0.0',
      packages=find_packages(),
      namespace_packages=['terraref'],
      include_package_data=True,
      url='https://github.com/terraref/ply2las',
      data_files = datafiles
      )
