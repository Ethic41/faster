#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-27 00:14:53
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0

from app.user import schemas as user_schemas

from app.utils.misc import gen_email, gen_random_str, gen_random_uuid
from app.utils.user import get_password_hash, verify_password


def gen_user() -> user_schemas.UserIn:
    return user_schemas.UserIn(
        email=gen_email(),
        firstname=gen_random_str(),
        lastname=gen_random_str(),
    )


def gen_user_update() -> user_schemas.UserUpdate:
    return user_schemas.UserUpdate(
        firstname=gen_random_str(),
        lastname=gen_random_str(),
        middlename=gen_random_str(),
        email=gen_email(),
    )


def gen_uuid() -> str:
    return gen_random_uuid()


def password_hash(password: str) -> str:
    return get_password_hash(password)


def verify_password_hash(password: str, password_hash: str) -> bool:
    return verify_password(password, password_hash)

