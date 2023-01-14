#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-06 14:32:47
# @Author  : Dahir Muhammad Dahir
# @Description : Based on bills fastapi template


from pydantic.fields import Field
from pydantic.networks import EmailStr
from app.utils.enums import ActionStatus, Gender
from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class BaseSchemaMixin(BaseModel):
    id: int
    uuid: str
    created_at: datetime
    last_modified: datetime

    class Config:
        orm_mode = True


class BaseUACSchemaMixin(BaseSchemaMixin):
    name: str
    description: Optional[str]


class Status(BaseModel):
    status: ActionStatus


class BaseSchemaMainMixin(BaseModel):
    id: int
    uuid: str
    created_at: datetime
    last_modified: datetime

    class Config:
        orm_mode = True

