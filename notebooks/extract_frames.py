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
import glob
import sys
import csv
import ffmpeg
import cv2
from os import listdir

# specify location of the datafiles
dirFp = r'/Volumes/My Passport/LeDoux/EXP003/T01/SAC1'

def get_datafiles(
    dir_fp: str,
    suffix = '.avi'
):
    """ Returns abs filepath for video files in a directory

    Parameters
    ----------
    dir_fp (str): Absolute path to the directory containing datafiles

    Returns
    ----------
    video_paths (list): List with all absolute paths for video datafiles
    """

    # Make sure path is valid
    assert os.path.isdir(dir_fp), "The path provided does not point to a directory."

    # Grab absolute filepaths of .avi videos
    filenames = listdir(dir_fp)
    video_paths = [os.path.abspath(filename) for filename in filenames if filename.endswith(suffix)]

    return video_paths

def load_csv(
    dir_fp: str
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
    df_cs['animal_id'] = df_cs['animal_id'].astype(str).apply(lambda x: x.zfill(6))
    df_framerate = pd.read_csv(dirFp+'/frame_rate.csv', index_col = 0)
    df_framerate['animal_id'] = df_framerate['animal_id'].astype(str).apply(lambda x: x.zfill(6))

    return df_cs, df_framerate

if __name__ == '__main__':
    videoPathList = get_datafiles(dirFp)
    dfMaster, dfFrameRate = load_csv(dirFp)
