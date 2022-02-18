################################################################################
# Filename: extract_frames.py
# Description: Extracts frames from .avi given frame start and end indices.
# Outputs:
# Author: Audrey Yin, ay2376@nyu.edu
# Created On: 2022-02-17 16:17:43
# Last Modified Date:
# Last Modified By:
################################################################################

# import modules
import pandas as pd
import numpy as np
import os
import sys
import csv
import ffmpeg
import cv2

# specify location of the datafiles
dirFp = r'/Volumes/My Passport/LeDoux/EXP003/T01/SAC1'

def load_csv(
    dir_fp: str,
):
    """ Load csv files into dataframes and preprocess timestamps

    Parameters
    ----------
    dir_fp (str): Absolute path to the directory containing datafiles

    Returns
    ----------
    df_cs (pd.DataFrame): Info of animal id, trial id, timestamps, frame indices
    df_framerate (pd.DataFrame): Info on video frame rate
    """
    # Make sure path is valid
    assert os.path.isdir(dir_fp), "The path provided does not point to a directory."

    # Pull data from csvs made in ts_preprocessing
    df_cs = pd.read_csv(dirFp+'/cs_timestamps.csv', index_col = 0)
    df_framerate = pd.read_csv(dirFp+'/frame_rate.csv', index_col = 0)

    return df_cs, df_framerate

if __name__ == '__main__':
    dfMaster, dfFrameRate = load_csv(dirFp)