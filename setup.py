from setuptools import find_packages, setup

setup(name='terraref-laser3d',
      version='1.0.0',
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
