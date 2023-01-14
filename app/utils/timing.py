#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-09 14:18:49
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from datetime import datetime, date, time, timedelta, timezone


def get_current_date() -> str:
    today = datetime.now(timezone(timedelta(hours=1)))
    return today.strftime("%Y-%m-%d")


def get_current_time() -> str:
    now = datetime.now(timezone(timedelta(hours=1)))
    return now.strftime("%I:%M:%S")


def get_current_datetime() -> datetime:
    return datetime.now(timezone(timedelta(hours=1)))

