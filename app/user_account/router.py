#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-09-20 18:15:08
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from typing import List
from fastapi import APIRouter, BackgroundTasks, Body, Query, Form, File, Path, UploadFile
from fastapi.param_functions import Depends

from sqlalchemy.orm.session import Session
from app.dependencies.dependencies import HasPermission, get_current_user, get_db
from app.issuance.schemas import IssuanceIn, IssuanceOut
from app.user.schemas import UserSchema
from app.user_account import cruds, schemas

uac_router = APIRouter(
    prefix="/user_account",
    tags=["User Account Endpoints"]
)

driver_router = APIRouter(
    prefix="/driver",
    tags=["Driver Endpoints"]
)

# ============[ Create Routes]============

@uac_router.post(
    "/create_by_image",
    response_model=schemas.UserAccountOut,
    dependencies=[Depends(HasPermission(["can_create_any_user_account"]))],
)
async def create_uac_by_image(
    db: Session = Depends(get_db),
    user_account: schemas.UserAccountByImage = Depends(),
    user_image: UploadFile = File(...),
    user: UserSchema = Depends(get_current_user)
):
    return cruds.create_uac_by_image(db, user_account, user_image, user)


@uac_router.post(
    "/create_by_nin",
    response_model=schemas.UserAccountOut,
    dependencies=[Depends(HasPermission(["can_create_any_user_account"]))],
)
async def create_uac_by_nin(
    db: Session = Depends(get_db),
    user_account: schemas.UserAccountByNIN = Body(...),
    user: UserSchema = Depends(get_current_user)
):
    return cruds.create_uac_by_nin(db, user_account, user)


@driver_router.post(
    "/create_by_image",
    response_model=schemas.DriverOut,
    dependencies=[Depends(HasPermission(["can_create_driver"]))],
)
async def create_driver_by_image(
    *,
    db: Session = Depends(get_db),
    driver: schemas.DriverCreateByImage = Depends(),
    driver_image: UploadFile = File(...),
    guarantor_image: UploadFile = File(...),
    user: UserSchema = Depends(get_current_user),
    bg_task: BackgroundTasks,
):
    return cruds.create_driver_by_image(db, driver, driver_image, guarantor_image, user, bg_task)


@driver_router.post(
    "/create_by_nin",
    response_model=schemas.DriverOut,
    dependencies=[Depends(HasPermission(["can_create_driver"]))],
)
async def create_driver_by_nin(
    db: Session = Depends(get_db),
    driver: schemas.DriverCreateByNIN = Depends(),
    guarantor_image: UploadFile = File(...),
    user: UserSchema = Depends(get_current_user)
):
    return cruds.create_driver_by_nin(db, driver, guarantor_image, user)


@driver_router.post(
    "/driver/issue_id",
    response_model=IssuanceOut,
    dependencies=[Depends(HasPermission(["can_issue_item"]))],
)
async def issue_driver_id(
    db: Session = Depends(get_db),
    issuance: IssuanceIn = Body(...),
    user: UserSchema = Depends(get_current_user)
):
    return cruds.issue_driver_id(db, issuance, user)


# ============[ Read Routes]============

@uac_router.get(
    "/any/{uac_uuid}",
    response_model=schemas.UserAccountOut,
    dependencies=[Depends(HasPermission(["can_view_any_user_account"]))],
)
async def get_uac_by_uuid(
    db: Session = Depends(get_db),
    uac_uuid: str = Path(...),
):
    return cruds.get_uac_by_uuid(db, uac_uuid)

@driver_router.get(
    "/id/{driver_uuid}",
    response_model=schemas.DriverFull,
    dependencies=[Depends(HasPermission(["can_view_driver"]))],
)
async def get_driver_by_uuid(
    db: Session = Depends(get_db),
    driver_uuid: str = Path(...),
):
    return cruds.get_driver_by_uuid(db, driver_uuid)


@driver_router.get(
    "/public/qr_verify/{unique_key}",
    response_model=schemas.DriverQRInfo,
)
async def public_view_driver_info(
    db: Session = Depends(get_db),
    unique_key: str = Path(...),
):
    return cruds.public_view_driver_info(db, unique_key)

# ============[ Update Routes]============

@driver_router.put(
    "/update/{driver_uuid}",
    response_model=schemas.DriverOut,
    dependencies=[Depends(HasPermission(["can_update_driver"]))],
)
async def update_driver(
    db: Session = Depends(get_db),
    driver: schemas.DriverUpdate = Body(...),
    driver_uuid: str = Path(...)
):
    return cruds.update_driver(db, driver, driver_uuid)


@driver_router.put(
    "/update/image/{driver_uuid}",
    response_model=schemas.DriverOut,
    dependencies=[Depends(HasPermission(["can_update_driver"]))],
)
async def update_driver_image(
    db: Session = Depends(get_db),
    driver_image: UploadFile = File(...),
    driver_uuid: str = Path(...)
):
    return cruds.update_driver_image(db, driver_image, driver_uuid)


# ============[ List Routes]============
@uac_router.get(
    "/list/all",
    response_model=schemas.UserAccountList,
    dependencies=[Depends(HasPermission(["can_view_all_user_account"]))],
)
async def list_all_uac(
    db: Session = Depends(get_db),
    filter: schemas.UserAccountFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
):
    return cruds.list_all_uac(db, filter, skip, limit)


@driver_router.get(
    "/list",
    response_model=schemas.DriverList,
    dependencies=[Depends(HasPermission(["can_list_driver"]))],
)
async def list_driver(
    db: Session = Depends(get_db),
    filter: schemas.DriverFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
):
    return cruds.list_driver(db, filter, skip, limit)


@driver_router.get(
    "/list/own",
    response_model=schemas.DriverList,
    dependencies=[Depends(HasPermission(["can_list_own_driver"]))],
)
async def list_own_driver(
    db: Session = Depends(get_db),
    filter: schemas.DriverFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
    user: UserSchema = Depends(get_current_user)
):
    return cruds.list_own_driver(db, filter, skip, limit, user)


# ============[ Delete Routes]============

@driver_router.delete(
    "/delete/{driver_uuid}",
    dependencies=[Depends(HasPermission(["can_delete_driver"]))],
)
async def delete_driver(
    db: Session = Depends(get_db),
    driver_uuid: str = Path(...),
):
    return cruds.delete_driver(db, driver_uuid)

