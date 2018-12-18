from setuptools import find_packages, setup

def description():
      with open('README.rst') as f:
            return f.read()

setup(name='terraref-laser3d',
      version='1.2.0',
      description='TERRA-REF laser 3D scanner science package',
      long_description=description(),
      keywords=['field crop', 'phenomics', 'computer vision', 'remote sensing'],
      classifiers=['Topic :: Scientific/Engineering :: GIS'],
      packages=find_packages(),
      namespace_packages=['terraref'],
      include_package_data=True,
      url='https://github.com/terraref/laser3d',
      install_requires=[
            'numpy',
            'scipy',
            'multiprocessing',
            'matplotlib',
            'Pillow',
            'laspy',
            'plyfile'
      ]
      )
