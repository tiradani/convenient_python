import time
import datetime

def epoch_from_string(self, input_dt_str, datetime_format="%Y-%m-%d %H:%M:%S %Z"):
    # give epoch in local time
    return time.mktime(time.strptime(input_dt_str, datetime_format))

def now_formatted(timestamp_format='%b %e %H:%M:%S'):
    return datetime.datetime.now().strftime(timestamp_format)
