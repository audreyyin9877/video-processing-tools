################################################################################
# Filename: ts_preprocessing.py
# Description: Preprocessing bonsai, arduino, and video datafiles to extract cs
#              timestamps and frame indexes, and to calculate framerate
# Outputs: cs__timestamps.csv, frame_rate.csv
# Author: Audrey Yin, ay2376@nyu.edu
# Created On: 2022-02-15 10:57:54
# Last Modified Date: 2022-02-17 16:02:02
# Last Modified By: Audrey Yin
################################################################################

#import modules
import pandas as pd
import numpy as np
import regex as re
import os # can also us os.system to call for ffmpeg
import sys
import csv

# specify location of the datafiles
dirFp = r'F:\LeDoux\EXP003\T01\SAC1'

# specify basename basename_extentions
basenameExtensions = {
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
    fp_dict (dict): Dictionary with all filepaths necessary for preprocessing csvs
        KEY = animal_id
        VALUE = list of bon_csv, ard_csv, vid_fp
            bon_csv = filepath for bonsai csv
            ard_csv = filepath for ard_csv
            vid_fp = filepath for avi
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
    """Check to see if datafiles are complete and usable. Includes:
        - Removing any empty strings in fp_dict
        - Checking to see if each animal_id key has three datafiles (2 .csv, 1 .avi)
        - Checking to see if ard_csv is complete

    Parameters
    ----------
    fp_dict (dict): Dictionary with all filepaths necessary for preprocessing csvs
        KEY = animal_id
        VALUE = list of bonsai, arduino, and video data filepaths

    Returns
    ----------
    prints string with error message, if existing
    """

    # Print message to user
    print();
    print("Checking if data is complete...")

    # Remove any empty strings within the dictionary
    for key in fp_dict:
        while "" in fp_dict[key]:
            fp_dict[key].remove("")

    for key in fp_dict:
        try:
            # Ensure that each animal_id has three datafiles
            check_datafiles = len(fp_dict[key])
            assert(check_datafiles == 3)

            # Ensure that all of arduino csv is complete
            log_data = pd.read_csv(fp_dict[key][1], names=['log', 'timestamp'])
            session_end_pat = 'SESSION > END'
            if session_end_pat in log_data.values:
                pass
            else:
                raise ValueError()
        except AssertionError:
            print(key, "is missing a datafile.")
            pprint.pprint(fp_dict[key])
            raise
        except ValueError:
            print("WARNING > FILE ERROR. Please verify content of arduino files for", key)
            ignore = input('Would you like to continue? [y/n]: ')
            check = 0
            while check == 0:
                if ignore == 'y':
                    check = 1
                    continue
                elif ignore == 'n':
                    check = 1
                    raise
                else:
                    ignore = input('Invalid input. Would you like to continue? [y/n]: ')
    print("All data complete.")

def load_csv(
    fp_dict: dict
) -> dict:
    """ Load csv files into dataframes and preprocess timestamps

    Parameters
    ----------
    fp_dict (dict): Dictionary with all filepaths necessary for preprocessing csvs
        KEY = animal_id
        VALUE = list of bonsai, arduino, and video data filpaths

    Returns
    ----------
    data_dict (dict): Dictionary with all csv data saved as a dataframe
        KEY = animal_id
        VALUE = list of df_bon and df_ard
            df_bon (pandas.DataFrame): timestamps of each video frame
            df_ard (pandas.DataFrame): timestamps of each arduino serial output
    """

    # instantiate a dictionary
    data_dict = {}

    # create and fill data_dict with dataframes from csv
    for key in fp_dict:
        # create arduino df from csv. Make timestamps datetime objects and set timestamps to index
        df_ard = pd.read_csv(fp_dict[key][1], names=['ard_output', 'timestamp'], date_parser='timestamp')
        df_ard.timestamp = pd.to_datetime(df_ard.timestamp)

        # create bonsai df from csv. Make timestamps datetime objects and set timestamps to index
        df_bon = pd.read_csv(fp_dict[key][0], names=['timestamp'], date_parser='timestamp')
        df_bon.timestamp = pd.to_datetime(df_bon.timestamp)
        df_bon = df_bon.reset_index().set_index('timestamp', drop=True)

        data_dict[key] = [df_bon, df_ard]

    return data_dict

def extract_cs_timestamps(
    data_dict: dict
) -> pd.DataFrame:
    """ Extracts and saves the timestamps when a CS occurs

    Parameters
    ----------
    data_dict (dict): Dictionary of dataframes from bonsai and arduino csvs
        KEY = animal_id
        VALUE = list of df_bon and df_ard

    Returns
    ----------
    df_cs (pandas.DataFrame): Dataframe containing columns:
        animal_id (str)
        cs_id (str): Trial 1, Trial 2, etc
        ts_start (DateTime): timestamp when a trial begins
        ts_end (DateTime): timestamp when trial ends
    """

    # print message to user
    print()
    print('Merging arduino and bonsai timestamps...')

    # instantiate empty lists. Appending list data is cheaper and requires less memory than appending dataframes
    animal_id = []
    cs_id = []
    ts_start = []
    ts_end = []

    # for each animal id, extract out id, timestamps, and trial id
    for key in data_dict:
        # pull df_ard out of dictionary
        df_ard = data_dict[key][1]

        # find animal_id
        animal_id.append(key)

        # find timestamps when CS > ON using regex
        cond = df_ard['ard_output'].str.contains('(CS > ON)')
        df_ts_start = df_ard[cond].drop(['ard_output'], axis=1)
        ts_start.append(df_ts_start['timestamp'].tolist())

        # find cs_id if CS was on. This prevents recording failed trials where no motion was detected
        extend_index = []
        index_ts_start = df_ts_start.index.tolist()
        for index in index_ts_start:
            above_one = index - 1
            above_two = index - 2
            extend_index.extend([above_one, above_two])
        index_ts_start.extend(extend_index)
        # create dataframe with trials only when CS occured. Find cs_id using regex
        df_search = df_ard.loc[index_ts_start].sort_index()
        cond = df_search['ard_output'].str.contains('(TRIAL NUMBER)')
        df_cs_id = df_search[cond]
        df_cs_id['ard_output'] = df_cs_id['ard_output'].map(lambda x: x.lstrip('TRIAL NUMBER ').rstrip(' > START'))
        df_cs_id['ard_output'] = df_cs_id['ard_output'].map(lambda x: 'TRIAL '+x if (len(x)==2) else 'TRIAL 0'+x)
        cs_id.append(df_cs_id['ard_output'].tolist())

        # find timestamps when CS > OFF using regex
        cond = df_ard['ard_output'].str.contains('(CS > OFF)')
        df_ts_end = df_ard[cond].reset_index().drop(['ard_output'], axis=1)
        ts_end.append(df_ts_end['timestamp'].tolist())

    # create final dataframe from lists
    df_cs = pd.DataFrame(zip(animal_id, cs_id, ts_start, ts_end), columns=['animal_id', 'cs_id', 'ts_start', 'ts_end'])
    df_cs = df_cs.set_index(['animal_id']).apply(pd.Series.explode).reset_index()

    return df_cs

def extract_acclimation_timestamps(
    data_dict: dict,
    df_cs: pd.DataFrame
) -> pd.DataFrame:
    """ Extracts and saves the timestamps during acclimation period. Adds to existing master dataframe (dfMaster)

    Parameters
    ----------
    data_dict (dict): Dictionary of dataframes from bonsai and arduino csvs
        KEY = animal_id
        VALUE = list of df_bon and df_ard
    df_cs (pandas.Dataframe): Dataframe containing columns:
        animal_id (str)
        cs_id (str): Trial 1, Trial 2, etc
        ts_start (DateTime): timestamp when a trial begins
        ts_end (DateTime): timestamp when trial ends

    Returns
    ----------
    df_cs (pandas.DataFrame): see above
    """

    # instantiate empty lists. Appending list data is cheaper and requires less memory than appending dataframes
    animal_id = []
    cs_id = []
    ts_start = []
    ts_end = []

    # for each animal id, extract out id, timestamps, and trial id
    for key in data_dict:
        # pull df_ard out of dictionary
        df_ard = data_dict[key][1]

        # find animal_id
        animal_id.append(key)

        # give cs_id
        cs_id.append('ACCLIMATION')

        # find timestamps when acclimation begins using regex
        cond = df_ard['ard_output'].str.contains('(ACCLIMATION)')
        df_ts_start = df_ard[cond].drop(['ard_output'], axis=1)
        ts_start.append(df_ts_start['timestamp'].tolist())

        # find timestamps when acclimation ends using regex
        cond = df_ard['ard_output'].str.contains('(TRIAL NUMBER 1 > START)')
        df_ts_end = df_ard[cond].reset_index().drop(['ard_output'], axis=1)
        ts_end.append(df_ts_end['timestamp'].tolist())

    # create dataframe for acclimation periods and place into a holder
    df_holder = pd.DataFrame(zip(animal_id, cs_id, ts_start, ts_end), columns=['animal_id', 'cs_id', 'ts_start', 'ts_end'])
    df_holder = df_holder.set_index(['animal_id']).apply(pd.Series.explode).reset_index()

    # join master dataframe with acclimation periods dataframe
    df_cs = pd.concat([df_holder, df_cs], ignore_index=True)

    # print message to user
    print('Merging timestamps done.')

    return df_cs

def get_frame_idx (
    data_dict: dict,
    df_cs: pd.DataFrame
) -> pd.DataFrame:
    """ Extract frame index from df_bon using ts_start and ts_end. Add to df_cs

    Parameters
    ----------
    data_dict (dict): Dictionary of dataframes from bonsai and arduino csvs
        KEY = animal_id
        VALUE = list of df_bon and df_ard
    df_cs (pandas.Dataframe): Dataframe containing columns:
        animal_id (str)
        cs_id (str): Trial 1, Trial 2, etc
        ts_start (DateTime): timestamp when a trial begins
        ts_end (DateTime): timestamp when trial ends

    Returns
    ----------
    df_cs (pandas.DataFrame): Dataframe containing new columns:
        frame_start (): frame index for ts_start
        frame_end (): frame index for ts_end
    """

    # print message to user
    print()
    print('Extracting video frame indices...')

    # create empty holder column to fill frame_start indices
    df_cs['holder'] = np.nan

    # for each animal, extract out the frame_start index
    for key in data_dict:
        # pull df_bon out of dictionary
        df_bon = data_dict[key][0]

        # iterate through the master dataframe to access ts_start and match to df_bon timestamps
        for i, row in enumerate(df_cs.itertuples(), 0):
            if key == row.animal_id:
                idx = df_bon.index.get_loc(row.ts_start, method='nearest')
                df_cs.loc[i, row.holder] = df_bon.index[idx-20]

    # BUG: When trying to fill holder column, indices seem to only fill column next. This is a cheap workaround... :(
    df_cs = df_cs.drop(['holder'], axis=1)
    df_cs = df_cs.set_axis([*df_cs.columns[:-1], 'frame_start'], axis=1, inplace=False)

    # repeated code to find frame_end
    df_cs['holder'] = np.nan
    for key in data_dict:
        # pull df_bon out of dictionary
        df_bon = data_dict[key][0]

        for i, row in enumerate(df_cs.itertuples(), 0):
            if key == row.animal_id:
                idx = df_bon.index.get_loc(row.ts_end, method='nearest')
                df_cs.loc[i, row.holder] = df_bon.index[idx+20]

    df_cs = df_cs.drop(['holder'], axis=1)
    df_cs = df_cs.set_axis([*df_cs.columns[:-1], 'frame_end'], axis=1, inplace=False)

    # print message to user
    print('Extracting indices done. ')

    return df_cs

def calculate_frame_rate(
    fp_dict: dict
) -> pd.DataFrame:
    """Calculate frame rate based on timestamp information

    Parameters
    ----------
    fp_dict (dict): Dictionary containing filepaths for the timestamp csv

    Returns
    ----------
    df_framerate (pd.DataFrame): Contains information on
        animal_id (str)
        mean_framerate (float): mean rounded to two decimals
        std_framerate (float): standard deviation rounded to two decimals
    """

    # print message to user
    print()
    print('Calculating frame rates...')

    # instantiate empty lists. Appending list data is cheaper and requires less memory than appending dataframes
    frame_rate = []

    # for every animal id, find the frame rate mean and std of their corresponding video
    for key in fp_dict:
        # read video timestamp csv and turn into dataframe
        bon_csv = fp_dict[key][0]
        df = pd.read_csv(bon_csv, names = ['timestamp'], parse_dates = True)

        # transform timestamps into timedelta objects represented in seconds
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc = False)
        df['timestamp'] = pd.to_timedelta(df['timestamp'].dt.strftime('%H:%M:%S')).dt.total_seconds().astype(int)

        # create a timedelta with the first timestamp
        df["net_timestamp"] = df["timestamp"] - df["timestamp"][0]

        # create a column of ones for each frame. Used to count total number of frames in each second
        df["frames_count"] = np.ones(len(df))

        # group timestamps together (== one second) and sum all frames in each grouped second
        df_1 = df.groupby("timestamp").sum().reset_index()

        # remove first and last elements. these are incomplete "seconds" and contain unreliable framerate measurements
        df_1.drop(index=[df_1.index.max(), df_1.index.min()], inplace=True)

        # calculate average frame rate and std
        mean = round(df_1['frames_count'].mean(), 2)
        std = round(df_1['frames_count'].std(), 2)

        # create a list for each animal_id and calculated mean + std
        frame_rate.append([key, mean, std])

    # print message to user
    print('Calculating frame rates done. ')

    # create dataframe from frame_rate (nested list)
    df_framerate = pd.DataFrame(frame_rate, columns=['animal_id', 'mean_framerate', 'std_framerate'])
    return df_framerate

def save_data(
    dir_fp: str,
    df_cs: pd.DataFrame,
    df_framerate: pd.DataFrame
):
    """Save a csv file with df_cs and df_framerate

    Parameters
    ----------
    dir_fp (str): Absolute path to the directory containing datafiles
    df_cs (pd.DataFrame): Info of animal id, trial id, timestamps, frame indices
    df_framerate (pd.DataFrame): Info on video frame rate
    """

    # print message to user
    print()
    print('Saving data to original filepath...')

    # sort master dataframe by animal_id and cs_id
    df_cs['animal_id'] = df_cs['animal_id'].astype(int)
    df_cs = df_cs.sort_values(['animal_id', 'cs_id']).reset_index(drop=True)

    # save master dataframe as a csv
    cs = os.path.join(dir_fp, 'cs_timestamps.csv')
    df_cs.to_csv(cs)
    print('CS timestamps and frames info saved at: ', cs)

    # sort framerate dataframe by animal_id
    df_framerate = df_framerate.sort_values('animal_id').reset_index(drop=True)

    # save framerate dataframe as a csv
    framerate = os.path.join(dir_fp, 'frame_rate.csv')
    df_framerate.to_csv(framerate)
    print('Frame rate info saved at:', framerate)


if __name__ == '__main__':
    # Grab raw data
    pathList = get_datafiles(dirFp, basenameExtensions)
    filepathDict = create_path_dict(pathList)
    check_datafile_complete(filepathDict)
    dataDict = load_csv(filepathDict)

    # Transform and extract timestamp data
    dfMaster = extract_cs_timestamps(dataDict)
    dfMaster = extract_acclimation_timestamps(dataDict, dfMaster)
    dfMaster = get_frame_idx(dataDict, dfMaster)

    # Extract metadeta on videos
    dfFrameRate = calculate_frame_rate(filepathDict)

    # Save data
    save_data(dirFp, dfMaster, dfFrameRate)
