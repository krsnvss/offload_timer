from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from misc import *
from datetime import datetime
from random import randint

# database connection
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName('offload.db')
db.open()


# Insert new record
def record_insert(_datetime, shift):
    _query = QSqlQuery()
    _query.exec_('''INSERT INTO main (dt, shift) VALUES ('{}', {})'''.format(_datetime, shift))
    print(_query.lastError().text())
    return True


# Unloads per shift
def shift_total():
    _day = shift_time(datetime.now())
    _query = QSqlQuery('''select count(*) 
        from main where dt between 
        datetime('{}') and datetime('{}')'''
        .format(_day[0],
                _day[1]))
    while (_query.next()):
        _total = _query.value(0)
    return _total


# Unloads per hour
def hour_total():
    _hour = one_hour(datetime.now())
    _query = QSqlQuery('''select count(*) 
        from main where dt between 
        datetime('{}') and datetime('{}')'''
        .format(_hour[0],
                _hour[1]))
    while (_query.next()):
        _total = _query.value(0)
    return _total


# Report data per hour
def hour_total_report(_datetime):
    _hour = one_hour(_datetime)
    _query = QSqlQuery('''select count(*) 
        from main where dt between 
        datetime('{}') and datetime('{}')'''
        .format(_hour[0],
                _hour[1]))
    while (_query.next()):
        _total = _query.value(0)
    return _total


# Report data per shift
def shift_data():
    _day = shift_time(datetime.now())
    _data = []
    _query = QSqlQuery('''select datetime(dt), shift from main 
        where dt between datetime('{}') and datetime('{}')'''
        .format(_day[0],
                _day[1]))
    while (_query.next()):
        _data.append([_query.value(0), _query.value(1)])
    return _data


# Save MES webapi token
def save_token(token, _datetime):
    _query = QSqlQuery()
    _query.exec_('''INSERT INTO tokens (token, expires) VALUES ("{}", '{}')'''.format(token, _datetime))
    return True


# Read MES webapi token
def read_token():
    _token = ''
    _query = QSqlQuery()
    _query.exec_('''select token from tokens
    where datetime(expires) > datetime('{}')'''.format(datetime.now()))
    while (_query.next()):
        _token = _query.value(0)
    if len(_token) > 1:
        return _token
    else:
        return None
