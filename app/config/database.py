#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-06 01:08:46
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import settings


engine = create_engine(
    settings.database_private_url, 
    pool_size=settings.database_pool_size, 
    max_overflow=settings.database_max_overflow,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
