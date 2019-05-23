from datetime import datetime, timedelta


# Calculate shift time
def shift_time(_datetime):
    if _datetime.hour < 8:
        _tomorrow = _datetime - timedelta(days=1)
        shift_start = datetime(year=_tomorrow.year,
                                month=_tomorrow.month,
                                day=_tomorrow.day,
                                hour=20,
                                minute=0,
                                second=0)
    elif _datetime.hour >=8 and _datetime.hour < 20:
        shift_start = datetime(year=_datetime.year,
                               month=_datetime.month,
                               day=_datetime.day,
                               hour=8,
                               minute=0,
                               second=0)
    else:
        shift_start = datetime(year=_datetime.year,
                               month=_datetime.month,
                               day=_datetime.day,
                               hour=20,
                               minute=0,
                               second=0)
    shift_finish = shift_start + timedelta(hours=11, minutes=59, seconds=59)
    return [shift_start, shift_finish]


# Finds out what shift is current for certain datetime
def one_hour(_datetime):
    hour_start = datetime(year=_datetime.year,
                         month=_datetime.month,
                         day=_datetime.day,
                         hour=_datetime.hour,
                         minute=0,
                         second=0)
    hour_finish = hour_start + timedelta(minutes=59, seconds=59)
    return [hour_start, hour_finish]


# Template for the output text file
def fill_txt(_shift, _hour, _limit, _countdown):
    _shift_add = 5 - len(str(_shift))
    _shift_lcd = ' '* _shift_add + str(_shift)
    _hour_add = 3 - len(str(_hour))
    _hour_lcd = ' '* _hour_add + str(_hour)
    lcd_text='''|СМЕНА|*|ЧАС|*|ЛИМИТ|
|-----|*|---|*|-----|
|{}|*|{}|*|{}|
|-----|*|---|*|-----|
*******|{}|*******
**осталось времени***'''.format(_shift_lcd,
                                 _hour_lcd,
                                 _limit,
                                 _countdown)
    return lcd_text
