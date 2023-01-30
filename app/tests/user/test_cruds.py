#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-26 19:32:32
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from pathlib import Path
from fastapi import HTTPException
from typing import Any
from pydantic import EmailStr
from app.user import cruds, schemas, models
from app.utils.crud_util import CrudUtil
from app.tests.utils.utils import gen_user, gen_user_update, gen_uuid, \
    verify_password_hash
import pytest

from app.utils.misc import gen_email, gen_random_password, gen_random_str

@pytest.fixture(scope="function")
def user(crud_util: CrudUtil) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
    )
    return user


@pytest.fixture(scope="function")
def admin_user(crud_util: CrudUtil, mock_account_create_mail: Any) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
        is_admin=True
    )
    return user


@pytest.fixture(scope="function")
def admin_users(
    crud_util: CrudUtil, 
    mock_account_create_mail: Any
) -> list[models.User]:
    users = []
    for i in range(5):
        user_data: schemas.UserIn = gen_user()
        user = cruds.create_user(
            crud_util,
            user_data,
            is_admin=True
        )
        users.append(user)
    return users


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


def test_create_admin_user(
    crud_util: CrudUtil, 
    create_account_mailbox: Path,
) -> Any:
    user_data: schemas.UserIn = gen_user()
    user = cruds.create_user(
        crud_util,
        user_data,
        is_admin=True
    )

    admin_password = create_account_mailbox.read_text().strip()

    assert verify_password_hash(admin_password, user.password_hash)
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
            gen_uuid(),
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
            gen_uuid(),
            user_data
        )


def test_delete_user(crud_util: CrudUtil, user: models.User) -> Any:
    cruds.delete_user(
        crud_util,
        user.uuid,
    )
    with pytest.raises(HTTPException):
        cruds.get_user_by_uuid(
            crud_util,
            user.uuid
        )


def test_delete_user_not_found(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException):
        cruds.delete_user(
            crud_util,
            gen_uuid(),
        )


def test_authenticate_user(
    crud_util: CrudUtil, 
    admin_user: models.User,
    create_account_mailbox: Path
) -> Any:
    
    admin_password = create_account_mailbox.read_text().strip()
    authenticated_user = cruds.authenticate_user(
        crud_util,
        EmailStr(admin_user.email),
        admin_password
    )

    assert authenticated_user.email == admin_user.email
    assert authenticated_user.uuid == admin_user.uuid


def test_authenticate_user_not_found(crud_util: CrudUtil) -> Any:
    with pytest.raises(HTTPException) as e:
        cruds.authenticate_user(
            crud_util,
            EmailStr(gen_email()),
            gen_random_password(),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "Email and password do not match"


def test_authenticate_user_wrong_password(
    crud_util: CrudUtil, user: models.User
) -> Any:
    with pytest.raises(HTTPException) as e:
        cruds.authenticate_user(
            crud_util,
            EmailStr(user.email),
            gen_random_password(),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "Email and password do not match"


def test_authenticate_inactive_user(
    crud_util: CrudUtil, 
    user: models.User,
) -> Any:

    cruds.update_user(
        crud_util,
        user.uuid,
        schemas.UserUpdate(
            is_active=False
        )
    )

    with pytest.raises(HTTPException) as e:
        cruds.authenticate_user(
            crud_util,
            EmailStr(user.email),
            gen_random_password(),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "User is not active"


def test_request_password_reset(
    crud_util: CrudUtil, 
    user: models.User,
    password_reset_mailbox: Path
) -> Any:

    response = cruds.request_password_reset(
        crud_util,
        EmailStr(user.email)
    )

    password_reset_link = password_reset_mailbox.read_text().strip()

    assert "reset-password" in password_reset_link
    assert response["detail"] == "We've sent a password reset link to your mail"


def test_request_password_reset_invalid_email(
    crud_util: CrudUtil,
) -> Any:

    response = cruds.request_password_reset(
        crud_util,
        EmailStr(gen_email())
    )

    assert response["detail"] == "We've sent a password reset link to your mail"


def test_reset_password(
    crud_util: CrudUtil, 
    user: models.User,
    password_reset_mailbox: Path,
    password_change_mailbox: Path,
) -> Any:

    cruds.request_password_reset(
        crud_util,
        EmailStr(user.email)
    )
    password_reset_link = password_reset_mailbox.read_text().strip()
    password_reset_token = password_reset_link.split("/")[-1]

    response = cruds.reset_password(
        crud_util,
        password_reset_token,
    )

    new_password = password_change_mailbox.read_text().strip()

    db_user = cruds.get_user_by_uuid(
        crud_util,
        user.uuid
    )

    assert "Password reset successful" in response["detail"]
    assert new_password in response["detail"]
    assert verify_password_hash(new_password, db_user.password_hash)


def test_reset_password_invalid_token(
    crud_util: CrudUtil, 
) -> Any:

    with pytest.raises(HTTPException) as e:
        cruds.reset_password(
            crud_util,
            gen_random_str(),
        )

    assert e.value.status_code == 400
    assert e.value.detail == "Invalid token"


def test_list_admin_users(
    crud_util: CrudUtil, 
    admin_users: list[models.User],
) -> Any:

    db_users: list[schemas.UserOut] = cruds.list_admin_users(
        crud_util,
        schemas.AdminUserFilter(),
    ).model_list

    assert admin_users[0].email in [user.email for user in db_users]


def test_list_admin_users_filter(
    crud_util: CrudUtil,
    admin_users: list[models.User],
) -> Any:

    db_users: schemas.UserList = cruds.list_admin_users(
        crud_util,
        schemas.AdminUserFilter(
            email=admin_users[0].email
        ),
        limit=1,
    )


    assert len(db_users.model_list) == 1
    assert db_users.model_list[0].email == admin_users[0].email


def test_change_admin_user_password(
    crud_util: CrudUtil,
    admin_user: models.User,
    password_change_mailbox: Path,
) -> Any:

    password_out = cruds.change_admin_password(
        crud_util,
        admin_user.uuid,
    )

    db_user = cruds.get_user_by_uuid(
        crud_util,
        admin_user.uuid
    )

    admin_password = password_change_mailbox.read_text().strip()

    assert verify_password_hash(admin_password, db_user.password_hash)
    assert admin_password == password_out.password


def test_change_admin_password_invalid_uuid(
    crud_util: CrudUtil,
) -> Any:

    with pytest.raises(HTTPException) as e:
        cruds.change_admin_password(
            crud_util,
            gen_uuid(),
        )

    assert e.value.status_code == 404
    assert e.value.detail == "User not found"

