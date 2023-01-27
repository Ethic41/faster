#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-26 19:32:32
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from fastapi import HTTPException
from typing import Any
from app.user import cruds, schemas
from app.utils.crud_util import CrudUtil
from app.tests.utils.utils import gen_user
import pytest

def test_create_user(crud_util: CrudUtil) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
    )
    assert user.email == user_data.email
    assert user.is_admin is False
    assert user.is_active is True
    assert hasattr(user, "id")
    assert hasattr(user, "password_hash")


def test_create_admin_user(crud_util: CrudUtil) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
        is_admin=True
    )
    assert user.email == user_data.email
    assert user.is_admin is True
    assert user.is_active is True
    assert hasattr(user, "id")
    assert hasattr(user, "password_hash")


def test_create_duplicate_user(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException):
        user_data: schemas.UserIn = gen_user()
        user = cruds.create_user(
            crud_util,
            user_data,
        )
        assert user.email == user_data.email

        user = cruds.create_user(
            crud_util,
            user_data,
        )

