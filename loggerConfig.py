import sys


def get_config(logfilename: str):
    CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'base': {
                'format': '%(asctime)s-%(name)-5s-%(levelname)-7s-%(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'base',
                'stream': sys.stdout,
            },
            'rich': {
                'class': 'rich.logging.RichHandler',
                'level': 'DEBUG',
                'formatter': 'base',
                'rich_tracebacks': True,
                'show_path': False,
                'show_time': False,
                'locals_max_length': None,
                'locals_max_string': None,
            },
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'base',
                'filename': logfilename,
                'when': 'H',
                'interval': 4,
                'backupCount': 10,
            },
            # Add more handlers here if necessary...
        },
        'loggers': {
            '': {  # root logger
                'level': 'DEBUG',
                'handlers': ['rich', 'file'],
            },
            'BENCH': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False,
            },
            'TEST': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False,
            },
            'TRAIN': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False,
            },
            # Add more loggers here if necessary...
        },
    }

    return CONFIG
