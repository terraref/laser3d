__author__ = 'weiqin'

import os
import sys
import subprocess
import pytest

from lasmerge.lasmerge import *

@pytest.fixture(scope='module')
def lasfile():
    return [os.path.join(os.path.dirname(__file__), 'data/newmerge1.las'), \
           os.path.join(os.path.dirname(__file__), 'data/newmerge2.las')]

def test_las_merge(lasfile):
    outfile = os.path.join(os.path.dirname(__file__), 'data/output.las')
    merge_las_by_name(lasfile, outfile)
    assert os.path.exists(outfile)
    outfileinfo = os.stat(outfile).st_size
    infilemaxinfo = max([os.stat(infile).st_size for infile in lasfile])
    assert infilemaxinfo <= outfileinfo
    os.remove(outfile)

if __name__ == '__main__':
    subprocess.call(['python -m pytest test_lasmerge.py -p no:cacheprovider'], shell=True)
