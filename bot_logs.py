# -*- coding: utf-8 -*-
# This example shows how the logger can be set up to use a custom JSON format.
import logging
import json
import traceback
from datetime import datetime
import json_logging
import sys

json_logging.ENABLE_JSON_LOGGING = True


class CustomJSONLog(logging.Formatter):
    """
    Customized logger
    """
    def get_exc_fields(self, record):
        if record.exc_info:
            exc_info = self.format_exception(record.exc_info)
        else:
            exc_info = record.exc_text
        return {f'{self.python_log_prefix}exc_info': exc_info}

    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def format(self, record):
        json_log_default = {"@timestamp": datetime.utcnow().isoformat(),
                        "level": record.levelname,
                        "message": record.getMessage(),
                        "caller": record.filename + '::' + record.funcName,
                            }
        json_log_object = {
            'python.logger_name': record.name,
            'python.module': record.module,
            'python.funcName': record.funcName,
            'python.filename': record.filename,
            'python.lineno': record.lineno,
            'python.thread': f'{record.threadName}[{record.thread}]',
            'python.pid': record.process
        }
        if hasattr(record, 'bot'):
            json_log_object.update(record.bot)

        if hasattr(record, 'opstack'):
            json_log_object.update(record.opstack)

        if record.exc_info or record.exc_text:
            json_log_object.update(self.get_exc_fields(record))

        json_log_default.update(json_log_object)
        return json.dumps(json_log_default)


def logger_init():
    json_logging.init(custom_formatter=CustomJSONLog)

# You would normally import logger_init and setup the logger in your main module - e.g.
# main.py
#logger_init()

#logger = logging.getLogger("test-logger")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler(sys.stdout))

#logger.info("test logging statement")
# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG