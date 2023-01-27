#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-26 19:32:32
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from fastapi import HTTPException
from typing import Any
from pydantic import EmailStr
from app.user import cruds, schemas, models
from app.utils.crud_util import CrudUtil
from app.tests.utils.utils import gen_user, gen_user_update
import pytest

@pytest.fixture(scope="module")
def user(crud_util: CrudUtil) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
    )
    return user


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

        cruds.create_user(
            crud_util,
            user_data,
        )


def test_get_user_by_email(crud_util: CrudUtil, user: models.User) -> Any:
    user = cruds.get_user_by_email(
        crud_util,
        EmailStr(user.email)
    )
    assert user.email == user.email
    assert hasattr(user, "id")


def test_get_user_by_email_not_found(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException):
        cruds.get_user_by_email(
            crud_util,
            EmailStr("somenonexistentmail@mail.com"),
        )


def test_get_user_by_uuid(crud_util: CrudUtil, user: models.User) -> Any:
    user = cruds.get_user_by_uuid(
        crud_util,
        user.uuid
    )
    assert user.uuid == user.uuid
    assert hasattr(user, "id")


def test_get_user_by_uuid_not_found(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException):
        cruds.get_user_by_uuid(
            crud_util,
            "somenonexistentuuid",
        )


def test_update_user(crud_util: CrudUtil, user: models.User) -> Any:
    user_data: schemas.UserUpdate = gen_user_update()
    
    # before update, they are not equal
    assert user.email != user_data.email
    assert user.firstname != user_data.firstname
    
    updated_user: models.User = cruds.update_user(
        crud_util,
        user.uuid,
        user_data
    )    

    # after update, they are equal
    assert updated_user.email == user_data.email
    assert updated_user.firstname == user_data.firstname


def test_update_user_not_found(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException):
        user_data: schemas.UserUpdate = gen_user_update()
        cruds.update_user(
            crud_util,
            "somenonexistentuuid",
            user_data
        )

