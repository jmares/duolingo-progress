import logging
from dl_lib import DLImport
import sqlite3
import os
import sys
import time
from datetime import datetime, date
from config import *

def get_log_file_mode(log_file):
    """
    Determine the file-mode for the log-file for weekday rotation
    :param log_file: path for the log-file
    :return: file-mode append or write, string
    """
    now = datetime.now()
    # check if log-file exists 
    if os.path.isfile(log_file):
        # if the log-file exists, compare the modified date to the current date
        file_date = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(log_file)))
        if file_date == now.strftime("%Y-%m-%d"):
            # if the modified date equals the current date, set file-mode to append
            file_mode = 'a'
        else:
            # if the modified date is different (older), set file-mode to (over)write
            file_mode = 'w'
    else:
        # if the log-file doesn't exist, set file-mode to write
        file_mode = 'w'

    return file_mode


def main():

    this_function = sys._getframe().f_code.co_name
    start_time = time.time()
    now = datetime.now()
    # create log file per weekday: duoprog_Wed.log
    log_file = LOG_DIR + 'duoprog_' + now.strftime('%a') + '.log'
    log_level = logging.DEBUG

    file_mode = get_log_file_mode(log_file)
    logging.basicConfig(filename=log_file, filemode=file_mode, 
        format='%(asctime)s - %(levelname)s : %(message)s', level=log_level)

    # START
    logging.info(f"{this_function}: start")

    dli = DLImport(DB_FILE, USERNAME, PASSWORD)

    dli.import_duo()
    dli.export_html(TEMPLATE_PAGE, WEB_PAGE)

    # END
    end_time = time.time()
    duration = str(round(end_time - start_time, 3))
    logging.info(f"{this_function}: time needed for script: {duration} seconds\n")
    logging.debug(f"{this_function}: stop main\n")


if __name__ == '__main__':
    main()
