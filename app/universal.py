# universal.py
# Some nice functions that can be used anywhere.
import datetime, time


def timestamp():
    """
    Gets the current timestamp in the form ("MM/DD/YYYY", "HH:MM:SS")
    """
    return str(datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %I:%M:%S %p'))