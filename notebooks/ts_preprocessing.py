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
import pprint
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

def create_path_dict (
    abspath_list: list
) -> dict:
    """ Create a dict with absolute filepaths for cs extraction.

    Parameters
    ----------
    abspath_list (list): List with all absolute paths for arduino, bonsai, and video datafiles

    Returns
    ----------
    fp_dict (dict): Dictionary with all filepaths aggregated.
        KEY = animal_id
        VALUE = list of arduino, bonsai, and video datafiles
    """

    # Make sure data format is correct and that the filepath exists
    for file in abspath_list:
        basename_tuple = ('_vid_ts_raw.csv', '_ard_ts_raw.csv', '.avi')
        print("Verifying filepath for", file, "...")
        assert file.endswith(basename_tuple), "File has an incorrect extension. Expected .csv or .avi"
        assert os.path.exists(file), "Filepath does not exist. Verify the absolute filepath"

    print("All filepaths are valid.")

    # Instantiate a dictionary
    fp_dict = {}

    # Fill dictionary with "animal_id:list of filepaths" pairs
    for file in abspath_list:
        # Extract animal ids from filepath name
        animal_id = re.search(r'_(\d{6})_', file)

        # Match animal id with corresponding csv and avi files
        bon_csv = [file for file in abspath_list
                   if file.endswith('_vid_ts_raw.csv') and animal_id.group() in file]
        ard_csv = [file for file in abspath_list
                   if file.endswith('_ard_ts_raw.csv') and animal_id.group() in file]
        vid_fp = [file for file in abspath_list
                  if file.endswith('.avi') and animal_id.group() in file]

        fp_dict[animal_id.group().replace('_', "")] = [''.join(bon_csv), ''.join(ard_csv), ''.join(vid_fp)]

    return fp_dict

def check_datafile_complete(
    fp_dict: dict
):
    """Remove any empty strings. Check to see if each animal_id keys have a list containing three datafiles

    Parameters
    ----------
    fp_dict (dict): Dictionary with all filepaths necessary for preprocessing csvs
        KEY = animal_id
        VALUE = list of arduino, bonsai, and video datafiles

    Returns
    ----------
    prints string with error message, if existing
    """
    # Remove any empty strings within the dictionary
    for key in fp_dict:
        while "" in fp_dict[key]:
            fp_dict[key].remove("")

    # Ensure that each animal_id has three datafiles
    try:
        for key in fp_dict:
            check_datafiles = len(fp_dict[key])
            assert(check_datafiles == 3)
    except AssertionError:
        print(key, "is missing a datafile.")
        pprint.pprint(fp_dict[key])

if __name__ == '__main__':
    abspath_list = get_datafiles(dir_fp, basename_extensions)
    dict = create_path_dict(abspath_list)
    check_datafile_complete(dict)
