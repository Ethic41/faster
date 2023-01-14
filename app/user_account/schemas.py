#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-09-20 17:22:39
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from pydantic.networks import EmailStr
from app.utils.enums import Gender, LicenseValidity
from app.mixins.commons import AssociationMin, ListBase, TaxItemTypeMin, DriverFull, UserAccountMin, UserMin, UserAccountPhone
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from app.mixins.schemas import BaseSchemaMixin
from app.utils.custom_validators import checkbirthdate, cleaned, uppercased
from datetime import date
from app.user.schemas import UserOut, UserIn


class NextOfKinCreate(BaseModel):
    firstname: str = Field(..., max_length=45, description="first name of next of kin")
    lastname: str = Field(..., max_length=45, description="last name of next of kin")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of next of kin")
    phone: str = Field(..., max_length=20, description="phone number of next of kin")
    address: str = Field(..., max_length=100, description="address of next of kin")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_address = uppercased("address")


class NextOfKinUpdate(BaseModel):
    firstname: Optional[str] = Field(None, max_length=45, description="first name of next of kin")
    lastname: Optional[str] = Field(None, max_length=45, description="last name of next of kin")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of next of kin")
    phone: Optional[str] = Field(None, max_length=20, description="phone number of next of kin")
    address: Optional[str] = Field(None, max_length=100, description="address of next of kin")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_address = uppercased("address")


class NextOfKinOut(BaseSchemaMixin):
    firstname: str = Field(..., max_length=45, description="first name of next of kin")
    lastname: str = Field(..., max_length=45, description="last name of next of kin")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of next of kin")
    phone: str = Field(..., max_length=20, description="phone number of next of kin")
    address: str = Field(..., max_length=100, description="address of next of kin")


class NextOfKinList(ListBase):
    result: List[NextOfKinOut]


class GuarantorCreate(BaseModel):
    firstname: str = Field(..., max_length=45, description="first name of guarantor")
    lastname: str = Field(..., max_length=45, description="last name of guarantor")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of guarantor")
    phone: str = Field(..., max_length=20, description="phone number of guarantor")
    address: str = Field(..., max_length=100, description="address of guarantor")
    image: str = Field(..., max_length=255, description="image of guarantor")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_address = uppercased("address")


class GuarantorUpdate(BaseModel):
    firstname: Optional[str] = Field(None, max_length=45, description="first name of guarantor")
    lastname: Optional[str] = Field(None, max_length=45, description="last name of guarantor")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of guarantor")
    phone: Optional[str] = Field(None, max_length=20, description="phone number of guarantor")
    address: Optional[str] = Field(None, max_length=100, description="address of guarantor")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_address = uppercased("address")


class GuarantorOut(BaseSchemaMixin):
    firstname: str = Field(..., max_length=45, description="first name of guarantor")
    lastname: str = Field(..., max_length=45, description="last name of guarantor")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of guarantor")
    phone: str = Field(..., max_length=20, description="phone number of guarantor")
    address: str = Field(..., max_length=100, description="address of guarantor")


class GuarantorList(ListBase):
    result: List[GuarantorOut]


class UserAccountByImage(BaseModel):
    user: UserIn
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    address: str = Field(..., max_length=255, description="Address of user")
    gender: Gender
    birthdate: date = Field(..., description="birthdate of user")
    next_of_kin: Optional[NextOfKinCreate] = Field(None)

    _val_address = uppercased("address")


class UserAccountByNIN(BaseModel):
    nin: str = Field(..., max_length=16, description="National Identity Number")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the vehicle owner")
    address: str = Field(..., max_length=255, description="Address of user")
    next_of_kin: Optional[NextOfKinCreate] = Field(None, description="next of kin details")


class UserAccountCreate(BaseModel):
    user_uuid: str = Field(..., description="unique id of user")
    next_of_kin_uuid: Optional[str] = Field(None, description="unique id of next of kin")
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    address: str = Field(..., description="address of user")
    image: str = Field(..., max_length=255, description="image of user")
    gender: Gender
    birthdate: date
    creator_uuid: str


class UserAccountUpdate(BaseModel):
    user_uuid: Optional[str] = Field(None, description="unique id of user")
    next_of_kin_uuid: Optional[str] = Field(None, description="unique id of next of kin")
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the user")
    address: Optional[str] = Field(None, description="address of user")
    image: Optional[str] = Field(None, max_length=255, description="image of user")
    gender: Optional[Gender] = Field(None)
    birthdate: Optional[date] = Field(None)


class UserAccountFilter(BaseModel):
    firstname: Optional[str] = Field(None, max_length=45)
    lastname: Optional[str] = Field(None, max_length=45)
    middlename: Optional[str] = Field(None, max_length=45)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    birthdate: Optional[date] = Field(None)


class UserAccountOut(BaseSchemaMixin):
    user_uuid: str = Field(..., description="unique id of user")
    next_of_kin_uuid: Optional[str] = Field(None, description="unique id of next of kin")
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    image: str = Field(..., max_length=255, description="image of user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    address: str = Field(..., description="address of user")
    gender: Gender
    birthdate: date

    user: UserMin


class UserAccountList(ListBase):
    result: List[UserAccountOut]


class DriverCreateByImage(BaseModel):
    firstname: str = Field(..., max_length=45, description="Firstname of the driver")
    lastname: str = Field(..., max_length=45, description="Lastname of the driver")
    middlename: Optional[str] = Field(None, max_length=45, description="Middlename of the driver")
    phone: str = Field(..., max_length=20, description="Phone number of the driver")
    address: str = Field(..., max_length=255, description="Address of vehicle owner")
    gender: Gender
    birthdate: date
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    vehicle_type_uuid: str = Field(..., description="Vehicle Type UUID")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    guarantor_firstname: str = Field(..., max_length=45, description="first name of next of kin")
    guarantor_lastname: str = Field(..., max_length=45, description="last name of next of kin")
    guarantor_middlename: Optional[str] = Field(None, max_length=45, description="middle name of next of kin")
    guarantor_phone: str = Field(..., max_length=20, description="phone number of next of kin")
    guarantor_address: str = Field(..., max_length=100, description="address of next of kin")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_complexion = uppercased("complexion")
    _val_address = uppercased("address")
    _val_association_number = uppercased("association_number")
    _clean_association_number = cleaned("association_number")
    _val_birthdate = checkbirthdate("birthdate")


class DriverCreateByNIN(BaseModel):
    nin: str = Field(..., max_length=16, description="National Identity Number")
    address: str = Field(..., max_length=255, description="Address of vehicle owner")
    vehicle_type_uuid: str = Field(..., description="Vehicle Type UUID")
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    # driving_license_number: Optional[str] = Field(None, max_length=45, description="driving license number of driver")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    guarantor_firstname: str = Field(..., max_length=45, description="first name of next of kin")
    guarantor_lastname: str = Field(..., max_length=45, description="last name of next of kin")
    guarantor_middlename: Optional[str] = Field(None, max_length=45, description="middle name of next of kin")
    guarantor_phone: str = Field(..., max_length=20, description="phone number of next of kin")
    guarantor_address: str = Field(..., max_length=100, description="address of next of kin")

    _val_complexion = uppercased("complexion")
    _val_address = uppercased("address")
    _val_association_number = uppercased("association_number")
    _clean_association_number = cleaned("association_number")


class DriverCreate(BaseModel):
    user_account_uuid: str = Field(..., description="unique id of user account")
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    # driving_license_number: Optional[str] = Field(None, max_length=45, description="driving license number of driver")
    expiry_date: date = Field(..., description="expiry date of driver")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    vehicle_type_uuid: str = Field(..., description="unique id of vehicle type")
    guarantor_uuid: str = Field(..., description="unique id of guarantor")
    unique_key: str = Field(..., description="Unique Key")
    qr_code_image: str = Field(..., max_length=255, description="qr code image of driver")
    creator_uuid: str = Field(..., description="unique id of creator")


class DriverUpdate(BaseModel):
    firstname: Optional[str] = Field(None, max_length=45, description="Firstname of the vehicle driver")
    middlename: Optional[str] = Field(None, max_length=45, description="Middlename of the vehicle driver")
    lastname: Optional[str] = Field(None, max_length=45, description="Lastname of the vehicle driver")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the vehicle driver")
    address: Optional[str] = Field(None, max_length=255, description="Address of vehicle driver")
    gender: Optional[Gender] = Field(None)
    birthdate: Optional[date] = Field(None)
    complexion: Optional[str] = Field(None, max_length=20, description="complexion of driver")
    vehicle_type_uuid: Optional[str] = Field(None, description="unique id of vehicle type")
    association_uuid: Optional[str] = Field(None, description="unique id of association")
    association_number: Optional[str] = Field(None, max_length=20, description="association number of driver")

    _val_firstname = uppercased("firstname")
    _val_lastname = uppercased("lastname")
    _val_middlename = uppercased("middlename")
    _val_complexion = uppercased("complexion")
    _val_address = uppercased("address")
    _val_association_number = uppercased("association_number")
    _clean_association_number = cleaned("association_number")
    _val_birthdate = checkbirthdate("birthdate")


class DriverFilter(BaseModel):
    gender: Optional[Gender] = Field(None)
    complexion: Optional[str] = Field(None, max_length=20, description="complexion of driver")
    phone: Optional[str] = Field(None, max_length=20)
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    association_number: Optional[str] = Field(None, max_length=20, description="association number of driver")
    vehicle_type_uuid: Optional[str] = Field(None, description="vehicle type uuid")
    association_uuid: Optional[str] = Field(None, description="association uuid")

    _val_association_number = uppercased("association_number")


class DriverOut(BaseSchemaMixin):
    user_account_uuid: str = Field(..., description="unique id of user account")
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    expiry_date: date = Field(..., description="expiry date of driver")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    vehicle_type_uuid: str = Field(..., description="unique id of vehicle type")
    guarantor_uuid: str = Field(..., description="unique id of guarantor")
    unique_key: str = Field(..., description="Unique Key")
    qr_code_image: str = Field(..., max_length=255, description="qr code image of driver")
    creator_uuid: str = Field(..., description="unique id of creator")

    user_account: UserAccountOut
    vehicle_type: TaxItemTypeMin
    association: AssociationMin
    creator: UserMin


class DriverList(ListBase):
    result: List[DriverOut]


class DriverPublicOut(BaseModel):
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    expiry_date: date = Field(..., description="expiry date of driver")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    vehicle_type_uuid: str = Field(..., description="unique id of vehicle type")

    vehicle_type: TaxItemTypeMin
    association: AssociationMin
    class Config:
        orm_mode = True


class DriverQRInfo(BaseModel):
    license_validity: LicenseValidity
    driver_info: DriverPublicOut

