################################################################################
# Filename: freezing.py
# Description:
# Outputs:
# Author: Audrey Yin, ay2376@nyu.edu
# Created On: 2022-07-07 15:01
# Last Modified Date:
# Last Modified By: Audrey Yin
################################################################################

import modules
import pandas as pd
import numpy as np
import regex as re
import os # can also us os.system to call for ffmpeg
import sys
import csv

# specify location of the datafiles
dirFp = r'/Users/audreyyin/Documents/LeDoux/Sample Data'

# specify basename basename_extentions
basenameExtensions = {
    'aoi': 'cs_timestamps.csv',
    'raw_coord': 'el_filtered.csv'
}
