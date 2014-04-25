import datetime
import dateutil.parser
import dateutil.relativedelta
import dateutil.tz
import time

def epoch_from_string(self, input_dt_str, datetime_format="%Y-%m-%d %H:%M:%S %Z"):
    # give epoch in local time
    return time.mktime(time.strptime(input_dt_str, datetime_format))

def now_formatted(timestamp_format='%b %e %H:%M:%S'):
    return datetime.datetime.now().strftime(timestamp_format)

def now_epoch():
    return time.mktime(datetime.datetime.utcnow().timetuple())

def now_datetime(utc=True):
    if utc:
        now = datetime.datetime.now(dateutil.tz.tzutc())
    else:
        now = datetime.datetime.now(dateutil.tz.tzlocal())

    return now

def time_from_timestamp(timestamp, utc=True):
    """
    Parse a timestamp with dateutil.parser.parse(), and set to the local
    timezone.  This is still usable for date math.
    """
    if timestamp is None:
        return False

    ts = dateutil.parser.parse(timestamp)
    if utc:
        local = ts.astimezone(dateutil.tz.tzutc())
    else:
        local = ts.astimezone(dateutil.tz.tzlocal())

    return local

def time_delta(cert_expiry_time, local_time):
    """
    It is expected that 'cert_expiry_time' and 'local_time' are dateutil objects
        years = rdelta.years
        months = rdelta.months
        days = rdelta.days

    """
    rdelta = dateutil.relativedelta.relativedelta(cert_expiry_time, local_time)
    return rdelta
