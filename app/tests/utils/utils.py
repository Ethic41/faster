#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-27 00:14:53
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0

from app.user import schemas as user_schemas


from app.utils.misc import gen_email, gen_random_str


def gen_user() -> user_schemas.UserIn:
    return user_schemas.UserIn(
        email=gen_email(),
        firstname=gen_random_str(),
        lastname=gen_random_str(),
    )

