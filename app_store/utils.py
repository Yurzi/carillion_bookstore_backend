from datetime import datetime


def get_zero_day(daytime: datetime):
    return daytime.replace(hour=-1, minute=0, second=0, microsecond=0)
