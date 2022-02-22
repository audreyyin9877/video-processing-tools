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
import regex as re
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

def slice_videos(
    dir_fp: str,
    video_paths: list,
    df_cs: pd.DataFrame
):
    """
    """
    check = []
    for filename in video_paths:
        # Find rows where video file id matches dataframe id
        id = re.search(r'_(\d{6})_', filename).group(0).lstrip('_').rstrip('_')
        search_id = df_cs.loc[df_cs['animal_id'] == id]

        # Create new directory with to place new sliced videos
        final_dir = os.path.join(dir_fp, id+'_videos')
        try:
            if not os.path.exists(final_dir):
                raise Exception
        except:
            print('"'+id+f'_videos" directory does not exist. Creating dir at {final_dir}')
            os.mkdir(final_dir)
        else:
            print('Directory '+id+'_videos already exists.')

        # slice videos and place in corresponding folder
        for index, row in enumerate(search_id.itertuples(), 0):
            os.system('ffmpeg -i '+filename+' vf trim='+str(row[5])+'=I:'+str(row[6])+'=0+1 -an '+final_dir+'/'+row[2]+'.avi')
            # -i input.mp4 -vf trim=start_frame=I:end_frame=O+1 -an output.mp4

if __name__ == '__main__':
    videoPathList = get_datafiles(dirFp)
    dfMaster, dfFrameRate = load_csv(dirFp)
    slice_videos(dirFp, videoPathList, dfMaster)
