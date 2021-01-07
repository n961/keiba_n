import logging
import logging.config
import logging.handlers
import configparser
import wineventlog
from multiprocessing import Process, Queue, Event, current_process
import os
from pathlib import Path

from logging import DEBUG, INFO, WARNING, ERROR

LOG_BASE_PATH = Path()

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)
    
    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        s = s.replace('\n', '')
        return s
    
    
q = Queue()
CONFIG_INITIAL_SCORING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed_one': {
            '()': OneLineExceptionFormatter,
            'format': '%(asctime)s, win-hourse scoring, %(levelname)s, %(name)s, %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed_one'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1000000,
            'backupCount': 3,
            'encoding': 'utf-8',
            'filename': str(LOG_BASE_PATH / 'win_hourse.log'),
            'mode': 'a',
            'formatter': 'detailed_one'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    }
}

CONFIG_INITIAL_TEL = {
    'version': 1,
    'desable_existing_loggers': True,
    'formatters': {
        'detailed_one': {
            '()': OneLineExceptionFormatter,
            'format': '%(asctime)s, win-hourse scoring, %(levelname)s, %(name)s, %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed_one'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1000000,
            'backupCount': 3,
            'encoding': 'utf-8',
            'filename': str(LOG_BASE_PATH / 'tel.log'),
            'mode': 'a',
            'formatter': 'detailed_one'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    }
}


CONFIG_WORKER = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'queue': {
            'class': 'logging.handlers.QueueHandler',
            'queue': q
        }
    },
    'root': {
        'handlers': ['queu'],
        'level': 'INFO'
    }
}

CONFIG_LISTENER = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed_one': {
            '()': OneLineExceptionFormatter,
            'format': '%(asctime)s, win-hourse scoring, %(levelname)s, %(name)s, %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed_one'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1000000,
            'backupCount': 3,
            'encoding': 'utf-8',
            'filename': str(LOG_BASE_PATH / 'win_hourse_auto.log'),
            'mode': 'a',
            'formatter': 'detailed_one'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    }
}


class MyHandler:
    def handle(self, record):
        if record.name == "root":
            logger = logging.getLogger()
        elif record.name == "papermill":
            logger = logging.getLogger("papermill")
            logger.setLevel(logging.WARNING)
        else:
            logger = logging.getLogger(record.name)
            
        if logger.isEnabledFor(record.levelno):
            logger.handle(record)
            
            
class Listner:
    def __init__(self):
        self.stop_event = Event()
        self.lp = Process(target=self.listener_process, name='listener', args=(q, CONFIG_LISTENER))
        self.lp.start()
    
    def listener_process(self, q, config):
        logging.config.dictConfig(config)
        listener = logging.handlers.QueueListener(q, MyHandler())
        listener.start()
        
        self.stop_event.wait()
        listener.stop()
    
    def stop_listener(self):
        self.stop_event.set()
        self.lp.join()


def init_logger(name='root'):
    LOG_BASE_PATH.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(CONFIG_WORKER)
    logger = logging.getLogger(name)
    return logger

def init_scoring_logger(name='notebook'):
    LOG_BASE_PATH.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(CONFIG_INITIAL_SCORING)
    logger = logging.getLogger(name)
    return logger

def init_tel_logger(name='notebook'):
    LOG_BASE_PATH.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(CONFIG_INITIAL_TEL)
    logger = logging.getLogger(name)
    return logger

def init_bat_logger(name='bat'):
    LOG_BASE_PATH.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(CONFIG_LISTENER)
    logger = logging.getLogger(name)
    return logger


msgconfig = configparser.ConfigParser()
msgconfig.read('logcode.ini')
event_log = wineventlog.WinEventLog()

def info_with_eventlog(logger, code, bookname='', addmessage=''):
    message = msgconfig['MSG'][code]
    addmessage = str(addmessage).replace(",", ";")
    logger.info(f"{message} {addmessage}")
    event_log.warning('2105', f"{bookname} {message} {addmessage}")