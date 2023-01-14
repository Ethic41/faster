#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-10 23:42:49
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


import re
from secrets import randbits, token_urlsafe
from datetime import datetime, timezone, timedelta, date
from typing import Dict, Optional
from app.mixins.commons import DateRange
from pathlib import Path
import requests
import calendar
from passlib import pwd # type: ignore

def gen_email(nin: str = ""):
    nin = nin or str(gen_random_nin())
    return f"{nin}@gmail.com"


def gen_random_password():
    return token_urlsafe(12)


def gen_random_str():
    return pwd.genphrase(10)


def gen_random_nin() -> int:
    return randbits(50)


def gen_random_phone() -> str:
    phone = f"{randbits(37)}"
    if len(phone) < 11:
        phone = f"{phone}{'1' * (11 - len(phone))}"
    if len(phone) > 11:
        phone = f"{phone[:11]}"
    return phone


def get_current_date() -> str:
    today = datetime.now(timezone(timedelta(hours=1)))
    return today.strftime("%Y-%m-%d")


def get_current_time() -> str:
    now = datetime.now(timezone(timedelta(hours=1)))
    return now.strftime("%I:%M:%S")


def date_diff(date1: date, date2: date):
    result = date1 - date2
    return result.days


def time_diff(time1: str, time2: str, format: str = "%I:%M:%S"):
    time_diff = datetime.strptime(time1, format) - datetime.strptime(time2, format)
    return time_diff.seconds


def date_days_add(date: date, days: int):
    return date + timedelta(days=days)


def get_today_date_range(column_name: str):
    return DateRange(column_name=column_name, from_date=get_current_date(), to_date=get_current_date())


def requester(
    url, 
    method: str = "get", 
    files: Optional[Dict] = None, 
    data: Optional[Dict] = None, 
    headers: Optional[Dict] = None,
    json: Optional[Dict] = None
) -> requests.Response:
    with requests.Session() as s:
        response = getattr(s, method)(url, files=files, data=data, json=json, headers=headers)
    
    return response


def get_last_str_number_part(number: str) -> int:
    search_result = re.search(r'\d+$', number)
    if not search_result:
        raise ValueError("string does not contain a number")
    
    return int(search_result.group())

def get_filename_from_path(path: str) -> str:
    return Path(path).name


def days_summary(days: int):
    if days == 0:
        return ""
    
    if days == 1:
        return f"{days} day"
    
    if days < 7:
        return f"{days} days"
    
    if days == 7:
        return f"{days // 7} week"
    
    if days < 30:
        return f"{days // 7} weeks {days_summary(days % 7)}"
    
    if days == 30:
        return f"{days // 30} month"
    
    if days < 365:
        return f"{days // 30} months {days_summary(days % 30)}"
    
    if days == 365:
        return f"{days // 365} year"
    
    return f"{days // 365} years {days_summary(days % 365)}"


def number_of_weekday_btw_dates(day_name: str, from_date: date, to_date: date) -> int:
    day_mapping = {"monday": calendar.MONDAY, "tuesday": calendar.TUESDAY, \
        "wednesday": calendar.WEDNESDAY, "thursday": calendar.THURSDAY, "friday": calendar.FRIDAY, \
        "saturday": calendar.SATURDAY, "sunday": calendar.SUNDAY}
    
    target_date = day_mapping[day_name.lower()]
    one_day = timedelta(days=1)
    count = 0
    
    while from_date <= to_date:
        if from_date.weekday() == target_date:
            count += 1
        from_date += one_day
    
    return count

