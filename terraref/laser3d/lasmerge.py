__author__ = 'weiqin'
import subprocess
import os


def merge_las_by_name(input_list, output):
    """
    input a list of las files location, the function will generate a merged las file to output directory
    :param input_list: list of location of input files
    :param output: string of output file location
    :return:no return needed
    """

    basedire = os.path.join(os.path.dirname(__file__),"LAStools","bin","lasmerge")
    inputform = ["-i "+s for s in input_list]
    inputform = " ".join(inputform)
    outputform = "-o " + output
    sp_input = [basedire+" "+ inputform +" "+outputform]
    FNULL = open(os.devnull, 'w')
    subprocess.call(["make clean"],shell=True, stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["make"],shell=True,stdout=FNULL, stderr=subprocess.STDOUT)
    subprocess.call(sp_input,shell=True,stdout=FNULL, stderr=subprocess.STDOUT)
