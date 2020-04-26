import os
import logging
from logging.handlers import RotatingFileHandler
from logging import getLogger
from flask import Flask

# Constants
APP_NAME = "Sample Flask App"
ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(ROOT, 'input_files')
ALLOWED_EXTENSIONS = {'xlsx'}
OUTPUT_FOLDER = os.path.join(ROOT, 'output_files')
APP_LOG = ROOT + '\\logs\\app_log.log'
LOG_FILE = ROOT + '\\logs\\app_log.log'
CACHE_LOG = ROOT + '\\logs\\cache.log'
GLOBAL_LOG = ROOT + '\\logs\\global_log.log'

# App Settings
app = Flask(__name__)
app.secret_key = "secretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# Logger Setup
log_format = '[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s-%(message)s'
logging.basicConfig(format = log_format, filename = GLOBAL_LOG, level = logging.DEBUG)
formatter = logging.Formatter(log_format,'%m-%d %H:%M:%S')

# File Handler Setup
fileHandler = logging.FileHandler(LOG_FILE)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

# Stream Handler Setup
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)

# Adding Handles to App 
app.logger.addHandler(fileHandler)
app.logger.addHandler(streamHandler)