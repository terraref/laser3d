import os
import logging
import shutil
import subprocess
import copy
import math
import laspy

merged_las = "/Users/weiqin/PycharmProjects/TerrarefDocs/scanner3DTop_lv1_2017-07-12__00-01-31-028_uamac_merged.las"
east_ply = "/Users/weiqin/PycharmProjects/TerrarefDocs/cd8a394f-1e09-45d6-aac7-3566ad8f900f__Top-heading-east_0.ply"
west_ply = "/Users/weiqin/PycharmProjects/TerrarefDocs/cd8a394f-1e09-45d6-aac7-3566ad8f900f__Top-heading-west_0.ply"
raw_data = "/Users/weiqin/PycharmProjects/TerrarefDocs/cd8a394f-1e09-45d6-aac7-3566ad8f900f_metadata.json"

