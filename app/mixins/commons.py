#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-24 00:40:54
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from app.utils.custom_validators import currency_out_val
from enum import Enum


from app.mixins.schemas import BaseSchemaMixin
from pydantic import BaseModel, Field, EmailStr
from datetime import date


class Gender(str, Enum):
    male = "m"
    female = "f"
    na = "na"


class WalletStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    closed = "closed"


class WalletTxnType(str, Enum):
    credit = "credit"
    debit = "debit"


class PaymentAccountStatus(str, Enum):
    activated = "activated"
    deactivated = "deactivated"
    blacklisted = "blacklisted"


class EnrollmentStatus(str, Enum):
    enrolled = "enrolled"
    not_enrolled = "not_enrolled"


class TaxPayerType(str, Enum):
    registered = "registered"
    unregistered = "unregistered"
class NINImageOut(BaseModel):
    nin: str = Field(..., max_length=16)
    image: str = Field(..., max_length=160)

    class Config:
        orm_mode = True


class UserOut(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: str | None = ''
    is_active: bool
    is_system_user: bool

    class Config:
        orm_mode = True


class VehicleQROut(BaseModel):
    qr_file: str

    class Config:
        orm_mode = True


class DateRange(BaseModel):
    column_name: str
    from_date: date
    to_date: date


class ListBase(BaseModel):
    count: int
    sum: float | None = Field(None)

    _val_sum = currency_out_val("sum")


class FilterBase(BaseModel):
    skip: int
    limit: int


class UserMin(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: str | None = ''


class UserAccountMin(BaseSchemaMixin):
    user_uuid: str = Field(..., description="unique id of user")
    next_of_kin_uuid: str | None = Field(None, description="unique id of next of kin")
    nin: str | None = Field(None, max_length=16, description="nin of user")
    image: str = Field(..., max_length=255, description="image of user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    address: str = Field(..., description="address of user")
    gender: Gender
    birthdate: date

    user: UserMin


class UserAccountPhone(BaseModel):
    phone: str = Field(..., max_length=20, description="Phone number of the user")

    class Config:
        orm_mode = True


class UserAccountFull(UserAccountMin):
    user: UserMin

