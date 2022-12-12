from datetime import datetime, date, timedelta


def get_diff_day(start, end=datetime.now()):
    if type(start) == datetime:
        d = start
    else:
        d = datetime.strptime(start[0:10], '%Y-%m-%d')
    return (d - end).days


def get_diff_selected(index):
    now = datetime.now()
    diffs = [-7, -30, get_diff_day(now - timedelta(days=now.weekday())), get_diff_day(datetime(now.year, now.month, 1)),
          get_diff_day(datetime(now.year, 1, 1))]
    return diffs[index]