#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-07 12:38:04
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext
import os


# Password hash context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT config
ALGORITHM = os.getenv("JWT_ALGORITHM")
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('TOKEN_LIFE_SPAN', default=""))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    verified: bool = pwd_context.verify(plain_password, hashed_password)
    return verified


def get_password_hash(password: str) -> str:
    hash: str = pwd_context.hash(password)
    return hash


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone(timedelta(hours=1))) + \
        timedelta(hours=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
