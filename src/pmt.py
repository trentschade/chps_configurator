# import xml.etree.ElementTree as ET
# import time
# import re
# import copy
# from datetime import datetime, date, time, timedelta
# import shlex
# import subprocess
# #import StringIO
# import sys
# import os
# import glob
# import gzip
# import shutil
# import unittest
# import argparse

from modparsing import *


root_dir = r"C:\Users\trent.schade\Desktop\Trent_Old_Files\Documents\dev\python\test\awips\chps_archive\data"
file_name = 'modifiers.xml'

pm = ParseMgmt()
pm.root_dir = root_dir
pm.file_name = file_name

pm.find_subdirs()
pm.make_mod_files()

#pm.count_all_files()

#pm.report_totals()

pm.move_rename_gzip()