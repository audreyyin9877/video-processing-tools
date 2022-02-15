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
