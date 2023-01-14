#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-06 13:46:25
# @Author  : Dahir Muhammad Dahir
# @Description : taken from Bill's template codebase


from datetime import date
from typing import Any
import ulid

import inflect

from sqlalchemy import Column, DateTime, Integer, String, Date
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import func


get_plural = inflect.engine()

def get_new_ulid() -> str:
    return ulid.new().str

class BaseMixin:
    '''
    Provides id, created_at and last_modified columns
    '''
    @declared_attr
    def __tablename__(cls: Any) -> str:
        try:
            cls.__tablename__
        except RecursionError:
            pass
        plural_name: str = get_plural.plural_noun(cls.__name__.lower())
        return plural_name

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(String(length=50), unique=True, nullable=False, default=get_new_ulid)
    date = Column(Date, index=True, default=date.today, nullable=True)
    created_at = Column(DateTime, index=True, server_default=func.now(), nullable=False)
    last_modified = Column( DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class BaseUACMixin(BaseMixin):
    '''
    Defines common columns for user access control models
    '''
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255))

