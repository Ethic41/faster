#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-06 01:08:46
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from os import getenv

load_dotenv()

CURRENT_ENV = getenv('LOCAL_DEV_ENV', default="False") 

DATABASE_USERNAME = getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")

if CURRENT_ENV == "True":
    DATABASE_SERVER_PRIVATE_ADDRESS = getenv("LOCAL_DATABASE_SERVER_PRIVATE_ADDRESS")
else:
    DATABASE_SERVER_PRIVATE_ADDRESS = getenv("REMOTE_DATABASE_SERVER_PRIVATE_ADDRESS")

DATABASE_PORT = getenv("DATABASE_PORT")
DATABASE_NAME = getenv("DATABASE_NAME")

DATABASE_URL = f"postgres://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER_PRIVATE_ADDRESS}:{DATABASE_PORT}/{DATABASE_NAME}" # noqa E501

# todo: the sizes should be set in config settings
engine = create_engine(DATABASE_URL, pool_size=50, max_overflow=85) # type: ignore

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
