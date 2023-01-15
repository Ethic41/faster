#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-06 14:32:47
# @Author  : Dahir Muhammad Dahir
# @Description : Based on bills fastapi template


from app.utils.enums import ActionStatus
from datetime import datetime, date as dt_date
from typing import Optional
from pydantic import BaseModel


class BaseSchemaMixin(BaseModel):
    id: int
    uuid: str
    date: dt_date
    created_at: datetime
    last_modified: datetime

    class Config:
        orm_mode = True


class BaseUACSchemaMixin(BaseSchemaMixin):
    name: str
    description: Optional[str]


class Status(BaseModel):
    status: ActionStatus

