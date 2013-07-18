'''
Created on Apr 25, 2013

@author: tiradani
'''
import os
import sys
import time
import syslog
import datetime
import logging

try:
    from colorama import Fore  # @UnresolvedImport
    from colorama import Style  # @UnresolvedImport
    COLORS_AVAILABLE = True
except:
    COLORS_AVAILABLE = False

from logging.handlers import TimedRotatingFileHandler

# create a place holder for a global logger, 
# individual modules can create their own loggers if necessary
log = None

class ColoredFormatter(logging.Formatter):
    def __init__(self, frmt, custom_colors=None):
        logging.Formatter.__init__(self, frmt)
        self.colors = {
            'WARNING': Fore.YELLOW,
            'INFO': Fore.WHITE,
            'DEBUG': Fore.BLUE,
            'CRITICAL': Fore.YELLOW,
            'ERROR': Fore.RED
        }
        if custom_colors is not None and isinstance(custom_colors, dict):
            self.colors.update(custom_colors)

    def colorize(self, msg_str, color):
        return color + msg_str + Style.RESET_ALL

    def format(self, record):
        levelname = record.levelname
        if levelname in self.colors:
            colorized_levelname = self.colorize(levelname, self.colors[levelname])
            record.levelname = colorized_levelname
        return logging.Formatter.format(self, record)

default_str = '[%(asctime)s] %(levelname)s:  %(message)s'
debug_str = '[%(asctime)s] %(levelname)s:::%(module)s::%(lineno)d: %(message)s'
COLORIZE_DEFAULT_FORMATTER = ColoredFormatter(default_str)
COLORIZE_DEBUG_FORMATTER = ColoredFormatter(debug_str)
DEFAULT_FORMATTER = logging.Formatter(default_str)
DEBUG_FORMATTER = logging.Formatter(debug_str)

# NOTE: The Console logger only understands message, level, and datetime 
#       substitutions
CONSOLE_FORMAT = '[%(datetime)s] %(level)s:  %(message)s'


syslog_priorities = {"EMERGENCY": syslog.LOG_EMERG,
                     "ALERT": syslog.LOG_ALERT,
                     "CRITICAL": syslog.LOG_CRIT,
                     "ERROR": syslog.LOG_ERR,
                     "WARNING": syslog.LOG_WARNING,
                     "NOTICE": syslog.LOG_NOTICE,
                     "INFO": syslog.LOG_INFO,
                     "DEBUG": syslog.LOG_DEBUG}

syslog_facilities = {"KERNEL": syslog.LOG_KERN,
                     "USER": syslog.LOG_USER,
                     "MAIL": syslog.LOG_MAIL,
                     "DAEMON": syslog.LOG_DAEMON,
                     "AUTH": syslog.LOG_AUTH,
                     "LPR": syslog.LOG_LPR,
                     "NEWS": syslog.LOG_NEWS,
                     "UUCP": syslog.LOG_UUCP,
                     "CRON": syslog.LOG_CRON,
                     "SYSLOG": syslog.LOG_SYSLOG,
                     "LOCAL0": syslog.LOG_LOCAL0,
                     "LOCAL1": syslog.LOG_LOCAL1,
                     "LOCAL2": syslog.LOG_LOCAL2,
                     "LOCAL3": syslog.LOG_LOCAL3,
                     "LOCAL4": syslog.LOG_LOCAL4,
                     "LOCAL5": syslog.LOG_LOCAL5,
                     "LOCAL6": syslog.LOG_LOCAL6,
                     "LOCAL7": syslog.LOG_LOCAL7}

syslog_options = {"LOG_PID": syslog.LOG_PID,
                  "LOG_CONS": syslog.LOG_CONS,
                  "LOG_NDELAY": syslog.LOG_NDELAY,
                  "LOG_NOWAIT": syslog.LOG_NOWAIT,
                  "LOG_PERROR": syslog.LOG_PERROR}

class LogError(Exception): pass

class SysLog(object):
    def __init__(self, option=syslog_options["LOG_PID"], 
                 facility=syslog_facilities["USER"],
                 timestamp_format='%b %e %H:%M:%S'):

        self.open_log(option, facility)
        self.timestamp_format = timestamp_format

    def set_timestamp_format(self, ts_format):
        self.timestamp_format = ts_format

    def open_log(self, option=syslog.LOG_PID, facility=syslog.LOG_USER):
        syslog.openlog(logoption=option, facility=facility)

    def log(self, priority, message):
        timestamp = datetime.datetime.now().strftime(self.timestamp_format)
        formatted_message = "%s: %s" % (timestamp, message)
        syslog.syslog(priority, formatted_message)

    def info(self, message):
        self.log(syslog.LOG_INFO, message)

    def warn(self, message):
        self.log(syslog.LOG_WARNING, message)

    def warning(self, message):
        self.warn(message)

    def error(self, message):
        self.log(syslog.LOG_ERR, message)

    def debug(self, message):
        self.log(syslog.LOG_DEBUG, message)

# Adding in the capability to use the built in Python logging Module
# This will allow us to log anything, anywhere
class TimedSizeHandler(TimedRotatingFileHandler):
    """
    Custom logging handler class that combines the decision tree for log 
    rotation from the TimedRotatingFileHandler with the decision tree from the 
    RotatingFileHandler.  This allows us to specify a lifetime AND file size to
    determine when to rotate the file.

    This class assumes that the lifetime specified is in days. (24 hour periods)

    @type filename: string
    @ivar filename: Full path to the log file.  Includes file name.
    @type interval: int
    @ivar interval: Number of days to keep log file before rotating
    @type maxBytes: int
    @param maxMBytes: Maximum size of the logfile in MB before file rotation 
    (used with min days)
    @type minDays: int
    @param minDays: Minimum number of days (used with max bytes)
    @type backupCount: int
    @ivar backupCount: How many backups to keep
    """

    def __init__(self, filename, interval=1, maxMBytes=10, minDays=0, 
                 backupCount=5):
        """
        Initialize the Handler.  We assume the following:

            1. Interval is in days
            2. No special encoding
            3. No delays are set
            4. Timestamps are not in UTC

        @type filename: string
        @param filename: The full path of the log file
        @type interval: int
        @param interval: Number of days before file rotation
        @type maxMBytes: int
        @param maxMBytes: Maximum size of the logfile in MB before file rotation
        @type backupCount: int
        @param backupCount: Number of backups to keep

        """
        #Make dirs if logging directory does not exist
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        when = 'D'
        TimedRotatingFileHandler.__init__(self, filename, when, interval, 
                                          backupCount, encoding=None)

        # Convert the MB to bytes as needed by the base class
        self.maxBytes = maxMBytes * 1024.0 * 1024.0

        # Convert min days to seconds
        self.minDays = minDays * 24 * 60 * 60

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        Basically, we are combining the checks for size and time interval

        @type record: string
        @param record: The message that will be logged.
        """
        do_timed_rollover = logging.handlers.TimedRotatingFileHandler.shouldRollover(self, record)
        min_day_time = self.rolloverAt - self.interval + int(time.time())
        do_size_rollover = 0
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if (self.stream.tell() + len(msg) >= self.maxBytes) and (min_day_time > self.minDays):
                do_size_rollover = 1

        return do_timed_rollover or do_size_rollover


def add_processlog_handler(logger_name, msg_types, 
                           maxDays, minDays, maxMBytes, 
                           log_dir="/var/log", colorize=False):
    """
    Adds a handler to the GlideinLogger logger referenced by logger_name.
    """
    logfile = os.path.expandvars("%s/%s.log" % (log_dir, logger_name))

    mylog = logging.getLogger(logger_name)
    mylog.setLevel(logging.DEBUG)

    handler = TimedSizeHandler(logfile, maxDays, minDays, maxMBytes, backupCount=5)
    if colorize:
        handler.setFormatter(COLORIZE_DEFAULT_FORMATTER)
    else:
        handler.setFormatter(DEFAULT_FORMATTER)
    handler.setLevel(logging.DEBUG)

    has_debug = False
    msg_type_list = [] 
    for msg_type in msg_types.split(","):
        msg_type = msg_type.upper().strip()
        if msg_type == "INFO":
            msg_type_list.append(logging.INFO)
        elif msg_type == "WARNING":
            msg_type_list.append(logging.WARN)
            msg_type_list.append(logging.WARNING)
        if msg_type == "ERROR":
            msg_type_list.append(logging.ERROR)
            msg_type_list.append(logging.CRITICAL)
        if msg_type == "DEBUG":
            msg_type_list.append(logging.DEBUG)
            has_debug = True

    if has_debug:
        if colorize:
            handler.setFormatter(COLORIZE_DEBUG_FORMATTER)
        else:
            handler.setFormatter(DEBUG_FORMATTER)

    handler.addFilter(MsgFilter(msg_type_list))

    mylog.addHandler(handler)
    
    return handler.stream.fileno()

class MsgFilter(logging.Filter):
    """
    Filter used in handling records for the info logs.
    """
    msg_type_list = [logging.INFO]
    
    def __init__(self, msg_type_list):
        logging.Filter.__init__(self)
        self.msg_type_list = msg_type_list
            
    def filter(self, rec):
        return rec.levelno in self.msg_type_list 

    
def format_dict(unformated_dict, log_format="   %-25s : %s\n"):
    """
    Convenience function used to format a dictionary for the logs to make it 
    human readable.
    
    @type unformated_dict: dict
    @param unformated_dict: The dictionary to be formatted for logging
    @type log_format: string
    @param log_format: format string for logging
    """
    formatted_string = ""
    for key in unformated_dict:
        formatted_string += log_format % (key, unformated_dict[key])

    return formatted_string

class ConsoleLog(object):
    def __init__(self, log_format=CONSOLE_FORMAT, timestamp_format="%b %e %H:%M:%S",
                 colorize=True, custom_colors=None):
        self.format = log_format
        self.timestamp_format = timestamp_format

        self.colorize = True
        self.colors = {
            'WARNING': Fore.YELLOW,
            'WARN': Fore.YELLOW,
            'INFO': Fore.WHITE,
            'DEBUG': Fore.BLUE,
            'CRITICAL': Fore.YELLOW,
            'ERROR': Fore.RED,
            'DEFAULT': Fore.BLACK,
            'RESET': Style.RESET_ALL
        }

        if custom_colors is not None and isinstance(custom_colors, dict):
            self.colors.update(custom_colors)

    def colorize_message(self, message, level):
        try:
            colorized = self.colors[level] + message + self.colors["RESET"]
        except IndexError:
            colorized = message

        return colorized

    def format_message(self, message, level):
        now = datetime.datetime.now()
        if self.colorize:
            message = self.colorize_message(message, level)

        sub_dict = {"datetime": now.strftime(self.timestamp_format),
                    "level": level,
                    "message": message}
        return self.format % sub_dict

    def set_timestamp_format(self, ts_format):
        self.timestamp_format = ts_format

    def log(self, level, message):
        level = level.upper()
        formatted_message = self.format_message(message, level)
        if level in ("CRITICAL", "ERROR"):
            print >> sys.stderr, formatted_message
        else:
            print >> sys.stdout, formatted_message

    def info(self, message):
        self.log("INFO", message)

    def warn(self, message):
        self.log("WARNING", message)

    def warning(self, message):
        self.warn(message)

    def error(self, message):
        self.log("ERROR", message)

    def debug(self, message):
        self.log("DEBUG", message)


class Log(object):
    """
    valid log types = "SYSLOG", "FILE", "CONSOLE"
    """
    def __init__(self, log_type, log_name=None, log_dir=None,
                 message_types="INFO,ERROR,WARNING,DEBUG",
                 max_days=7,
                 min_days=1,
                 max_mbytes=100,
                 option=syslog_options["LOG_PID"], 
                 facility=syslog_facilities["USER"],
                 colorize=False,
                 custom_colors=None,
                 timestamp_format='%b %e %H:%M:%S'):

        self.log_type = log_type
        if log_type.upper() == "SYSLOG":
            self.logger = SysLog(option=option, facility=facility,
                                 timestamp_format=timestamp_format)

        elif log_type.upper() == "FILE":
            if not os.path.isdir(log_dir):
                raise LogError("No such log directory: %s" % str(log_dir))
            if not log_name:
                raise LogError("Invalid log name: %s" % str(log_name))

            add_processlog_handler(log_name, log_dir, message_types,
                       max_days, min_days, max_mbytes, colorize=colorize)

            self.logger = logging.getLogger(log_name)

        elif log_type.upper() == "CONSOLE":
            self.logger = ConsoleLog(log_format=CONSOLE_FORMAT, 
                                     timestamp_format="%b %e %H:%M:%S",
                                     colorize=True, 
                                     custom_colors=custom_colors)

    def log(self, priority, message):
        if self.log_type == "SYSLOG":
            self.logger.log(priority, message)
        elif self.log_type == "FILE":
            if priority == "INFO":
                self.logger.info(message)
            elif priority == "ERROR":
                self.logger.error(message)
            elif priority == "WARNING":
                self.logger.warning(message)
            elif priority == "DEBUG":
                self.logger.debug(message)
            else:
                pass
        elif self.log_type == "CONSOLE":
            self.logger.log(priority, message)

    def log_info(self, message):
        if self.log_type == "SYSLOG":
            self.log(syslog.LOG_INFO, message)
        elif self.log_type in ("FILE", "CONSOLE"):
            self.log("INFO", message)

    def log_warn(self, message):
        if self.log_type == "SYSLOG":
            self.log(syslog.LOG_WARNING, message)
        elif self.log_type in ("FILE", "CONSOLE"):
            self.log("INFO", message)

    def log_error(self, message):
        if self.log_type == "SYSLOG":
            self.log(syslog.LOG_ERR, message)
        elif self.log_type in ("FILE", "CONSOLE"):
            self.log("INFO", message)

    def log_debug(self, message):
        if self.log_type == "SYSLOG":
            self.log(syslog.LOG_DEBUG, message)
        elif self.log_type in ("FILE", "CONSOLE"):
            self.log("INFO", message)
