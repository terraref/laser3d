__author__ = 'weiqin'

import os
import subprocess
from terraref.laser3d import generate_tif_from_las

dire = os.path.join(os.path.dirname(__file__), 'data/')
input = dire + 'newmerge1.las'
output = dire+'newmerge1.tif'

def test_las_to_tif():
    generate_tif_from_las(input, output)
    assert os.path.isfile(output)
    os.remove(output)

if __name__ == '__main__':
    subprocess.call(['python -m pytest test_las2dem.py -p no:cacheprovider'], shell=True)

