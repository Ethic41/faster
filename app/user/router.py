#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-09-19 22:37:46
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from typing import Any
from fastapi.param_functions import Path
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from app.access_control.cruds import get_group_by_name
from app.dependencies import dependencies as deps
from app.user import cruds, schemas, models
from app.utils.crud_util import CrudUtil
from app.utils.misc import gen_random_password
from app.utils.user import get_password_hash, create_access_token
from app.utils.mail import send_dummy_mail

load_dotenv()

users_router = APIRouter(
    prefix='/users',
    tags=['User'],
    dependencies=[Depends(deps.get_current_user)]
)

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@auth_router.post(
    '/docs-token', 
    include_in_schema=False
)
def docs_authentication(
    cu: CrudUtil = Depends(CrudUtil),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> schemas.Token:

    user = cruds.authenticate_user(
        cu=cu,
        email=EmailStr(form_data.username),
        password=form_data.password
    )

    token_data_to_encode = {
        'data': {
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'permissions': user.permissions
        }
    }
    access_token = create_access_token(token_data_to_encode)
    return schemas.Token(access_token=access_token, token_type='bearer')


@auth_router.post(
    '/token',
    response_model=schemas.Token,
)
def login(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    user_data: schemas.Login,
) -> schemas.Token:

    user: schemas.UserSchema = cruds.authenticate_user(
        cu,
        EmailStr(user_data.email),
        user_data.password,
    )

    token_data_to_encode = {
        'data': {
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'user_group': user.groups[0].name,
        }
    }

    access_token = create_access_token(token_data_to_encode)
    return schemas.Token(
        access_token=access_token,
        token_type='bearer',
        permissions=user.permissions,
    )


@auth_router.post(
    '/forgot-password',
)
def request_password_reset(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    email: EmailStr,
) -> dict[str, Any]:
    
    return cruds.request_password_reset(cu, email)


@auth_router.post(
    '/reset-password/{reset_token}'
)
def reset_password(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    reset_token: str,
) -> dict[str, Any]:

    return cruds.reset_password(cu, reset_token)


@users_router.post('',
    status_code=201,
    dependencies=[Depends(deps.HasPermission(["admin:create"]))]
)
def create_admin_user(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    user_data: schemas.UserIn,
) -> schemas.UserSchema:
    
    return cruds.create_user(cu, user_data, is_admin=True)


@users_router.get(
    '', 
    response_model=schemas.UserList,
    dependencies=[Depends(deps.HasPermission(["admin:list"]))]
)
def list_admin_users(
    cu: CrudUtil = Depends(CrudUtil),
    filter: schemas.AdminUserFilter = Depends(),
    skip: int = 0,
    limit: int = 100
):
    return cruds.list_admin_users(cu, filter, skip=skip, limit=limit)


@users_router.get(
    '/{uuid}', 
    response_model=schemas.UserSchema,
    dependencies=[Depends(deps.HasPermission(["can_view_system_user_details"]))]
)
def user_detail(uuid: str, dba: Session = Depends(deps.get_db)):
    user = cruds.get_user_by_uuid(uuid=uuid, db=dba)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    return user


@users_router.put(
    '/{uuid}', 
    response_model=schemas.UserSchema,
    dependencies=[Depends(deps.HasPermission(["can_update_system_user"]))]
)
def update_user(
    uuid: str,
    user_data: schemas.UserUpdate,
    dba: Session = Depends(deps.get_db)
):
    user = cruds.get_user_by_uuid(uuid=uuid, db=dba)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    user_update_dict = user_data.dict(exclude_unset=True)
    if len(user_update_dict) < 1:
        raise HTTPException(
            status_code=400,
            detail='Invalid request'
        )

    for key, value in user_update_dict.items():
        setattr(user, key, value)
    dba.commit()
    dba.refresh(user)
    return user


@users_router.put(
    "/change_password/{user_uuid}",
    dependencies=[Depends(deps.HasPermission(["admin:update"]))]
)
def change_admin_password(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    bg_task: BackgroundTasks,
    user_uuid: str = Path(...),
) -> schemas.PasswordChangeOut:

    return cruds.change_admin_password(cu, user_uuid, bg_task)


@users_router.delete(
    '/{uuid}',
    dependencies=[Depends(deps.HasPermission(["can_delete_system_user"]))]
)
def delete_user(uuid: str, dba: Session = Depends(deps.get_db)):
    user = cruds.get_user_by_uuid(db=dba, uuid=uuid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    dba.query(models.User). \
        filter(models.User.uuid == uuid). \
        delete()
    dba.commit()
    return {'detail': 'User deleted successfully.'}


@users_router.post(
    '/{uuid}/groups',
    response_model=schemas.UserSchema,
    dependencies=[Depends(deps.HasPermission(["can_change_system_user_group"]))]
)
def add_group_to_user(
    uuid: str, groups: schemas.UserGroup, dba: Session = Depends(deps.get_db)
):
    user = cruds.get_user_by_uuid(db=dba, uuid=uuid)
    group_list = groups.dict().pop('groups')
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    for group_name in group_list:
        group = get_group_by_name(name=group_name, db=dba)
        if not group:
            raise HTTPException(
                status_code=404,
                detail=f'{group_name} is not found'
            )
        user.groups.append(group)
    dba.commit()
    dba.refresh(user)
    return user


@users_router.delete(
    '/{uuid}/groups',
    response_model=schemas.UserSchema,
    dependencies=[Depends(deps.HasPermission(["can_change_system_user_group"]))]
)
def remove_group_from_user(
    uuid: str, groups: schemas.UserGroup, dba: Session = Depends(deps.get_db)
):
    user = cruds.get_user_by_uuid(db=dba, uuid=uuid)
    group_list = groups.dict().pop('groups')
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    for group_name in group_list:
        group = get_group_by_name(name=group_name, db=dba)
        if not group:
            raise HTTPException(
                status_code=404,
                detail=f'{group_name} is not found'
            )
        user.groups.remove(group)
    dba.commit()
    dba.refresh(user)
    return user


# @users_router.post('/{uuid}/password')
# def change_user_password(
#     uuid: str,
#     passwords: schemas.ChagePasswordFromDashboard,
#     dba: Session = Depends(deps.get_db)
# ):
#     user = cruds.get_user_by_uuid(db=dba, uuid=uuid)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail='User not found'
#         )
#     if not verify_password(passwords.current_password, user.password_hash):
#         raise HTTPException(
#             status_code=403,
#             detail='Current password is incorrect'
#         )
#     new_password_hash = get_password_hash(passwords.new_password)
#     user.password_hash = new_password_hash
#     dba.commit()
#     dba.refresh(user)
#     return {'detail': 'Password changed successfully.'}
