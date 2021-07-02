import logging
from dl_lib import DLImport
import sqlite3
from time import time
from datetime import datetime, date
from config import *

# Configuration
t1 = time()
now = datetime.now()
log_file = LOG_DIR + 'duolingo_' + now.strftime('%a') + '.log'

log_level = logging.INFO
#logging.basicConfig(filename= log_file, format='%(asctime)s - %(levelname)s : %(message)s', level=log_level)
if (now.strftime('%H') in ('00', '01', '02', '03', '04', '05', '06', '07')):
    fmode = 'w'
else:
    fmode = 'a'
logging.basicConfig(filename=log_file, filemode=fmode, format='%(asctime)s - %(levelname)s : %(message)s', level=log_level)

# START

logging.debug('starting main')

dli = DLImport(DB_FILE, USERNAME, PASSWORD)

dli.import_duo()
dli.export_html(TEMPLATE_PAGE, WEB_PAGE)

t2 = time()
tn = 'time needed for script: ' + str(round(t2 - t1, 3)) + ' seconds\n\n'
logging.info(tn)
logging.debug('stopping main')
