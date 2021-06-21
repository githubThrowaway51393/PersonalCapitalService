import os
import sys
from datetime import datetime, timedelta
from dateutil import relativedelta

def main():
    print(get_first_of_this_month("%Y%m%d"))
    print(get_last_of_this_month("%Y%m%d"))

def get_last_of_last_month(str_format):
    today = datetime.now()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    return lastMonth.strftime(str_format)
    
def get_first_of_last_month(str_format):
    today = datetime.now()
    first = today.replace(day=1)
    lastMonth = first - relativedelta.relativedelta(months=1)
    return lastMonth.strftime(str_format)
    
def get_last_of_this_month(str_format):
    today = datetime.now()
    first = today.replace(day=1)
    thisMonth = first + relativedelta.relativedelta(months=1) - timedelta(days=1)
    return thisMonth.strftime(str_format)
    
def get_first_of_this_month(str_format):
    today = datetime.now()
    first = today.replace(day=1)
    return first.strftime(str_format)
    
def convert_date_from_string(from_format, date_time): 
    format = from_format # The format 
    datetime_str = datetime.strptime(date_time, format) 
    return datetime_str

def convert_date_to_string(to_format, date_time): 
    return date_time.strftime(to_format)      

def date_is_between(date_to_check, start, end):
    res = False
    start_date = convert_date_from_string('%Y%m%d', start)
    end_date = convert_date_from_string('%Y%m%d', end)
    check_date = convert_date_from_string('%Y%m%d', date_to_check)
    if start_date <= check_date <= end_date:
        res = True
    return res
    
def reformat_date(date, from_format, to_format):
    date = convert_date_from_string(from_format, date)
    return date.strftime(to_format)
    
def reformat_timestamp(ts, to_format):
    ts = int(ts)
    ts = datetime.fromtimestamp(ts).strftime(to_format)
    return ts
    

if __name__ == '__main__':
    main()
    
   