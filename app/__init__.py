from flask import Flask, render_template, abort
import logging.handlers, os, sys

app = Flask(__name__, instance_relative_config=True)

# V1.0 : copy from student-booklet
# V1.1 : bugfix service-start-file
# V1.2 : small bugfixes

app.config['version'] = 'V1.2'

# enable logging
LOG_HANDLE = 'soauth'
log = logging.getLogger(LOG_HANDLE)

# local imports
from config import app_config


# support custom filtering while logging
class MyLogFilter(logging.Filter):
    def filter(self, record):
        record.username = 'NONE'
        return True

config_name = os.getenv('FLASK_CONFIG')
config_name = config_name if config_name else 'production'

# set up logging
LOG_FILENAME = os.path.join(sys.path[0], app_config[config_name].STATIC_PATH, 'log/soauth-log.txt')
try:
    log_level = getattr(logging, app_config[config_name].LOG_LEVEL)
except:
    log_level = getattr(logging, 'INFO')
log.setLevel(log_level)
log.addFilter(MyLogFilter())
log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 * 1024, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(username)s - %(message)s')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)

log.info('start SOAUTH')

app.config.from_object(app_config[config_name])
app.config.from_pyfile('config.py')

from app.view.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
