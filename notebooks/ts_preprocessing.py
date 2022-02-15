################################################################################
# Filename: ts_preprocessing.py
# Description: Preprocessing bonsai, arduino, and video datafiles to extract cs
#              ttls and calculate framerate
# Author: Audrey Yin, ay2376@nyu.edu
# Created On: 2022-02-15 10:57:54
# Last Modified Date:
# Last Modified By:
################################################################################

#import modules
import pandas as pd
import numpy as np
import regex as re
import os # can also us os.system to call for ffmpeg
import sys
import csv
import ffmpeg # can also use ffmpy, python wrapper for ffmpeg
import cv2
from matplotlib import pyplot as plt

# specify location of the datafiles
dir_fp = r'C:\Users\ay2376\Desktop\T01\_renamed'

# specify basename basename_extentions
basename_extensions = {
    'video': '.avi',
    'arduino_ts': 'ard_ts_raw.csv',
    'bonsai_ts': 'vid_ts_raw.csv'
}

def get_datafiles(
    dir_fp: str,
    basename_extensions: dict,
) -> list:
    """ Returns abs filepath for all arduino, bonsai, and video files in a directory

    Parameters
    ----------
    dir_fp (str): Absolute path to the directory containing datafiles
    basename_extensions (dict): basename identifies as keys and extensions as values
        MUST CONTAIN the keys: video, arduino_ts, bonsai_ts

    Returns
    ----------
    abspath (list): List with all absolute paths for arduino, bonsai, and video datafiles
    """

    # Make sure path is valid
    assert os.path.isdir(dir_fp), "The path provided does not point to a directory."

    # Check contents of the directory
    dirname, _, basename_list = next(os.walk(dir_fp))

    # Get the absolute paths for the entire content of the directory
    raw_abspath_list = [os.path.join(dirname, basename)
                        for basename in basename_list]

    # Filter  the abspath in the directory in order to get datafiles
    abspath_list = [os.path.abspath(file) for file in raw_abspath_list
                    if file.endswith(basename_extensions.get('video'))
                    or file.endswith(basename_extensions.get('arduino_ts'))
                    or file.endswith(basename_extensions.get('bonsai_ts'))]

    # Return list of abs paths
    return abspath_list

if __name__ == '__main__':
    list = get_datafiles(dir_fp, basename_extensions)
    print(list)
