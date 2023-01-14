#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-09-20 22:25:23
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from app.issuance.models import Issuance
from app.issuance.schemas import IssuanceCreate, IssuanceIn
from app.utils.enums import LicenseValidity
from os import getenv
from typing import Optional, Union
from app.utils.misc import gen_email, gen_random_password
from app.dependencies.dependencies import get_recognition_auth_token
from datetime import date, datetime, timedelta
from app.utils.nin import gen_user_from_nin
import ulid
from app.nin.cruds import general_get_user_by_nin, get_user_by_nin
from app.nin.models import NIN
from app.recognition.cruds import check_for_single_face, create_person, detect_single_face, get_face_id, index_face_to_collection
from app.utils.image_qr import create_and_upload_qr_cloud, upload_image_file_to_cloud, upload_remote_image_to_cloud
from fastapi import BackgroundTasks, UploadFile, HTTPException
from app.user.schemas import UserIn, UserSchema, UserUpdate
from app.user.cruds import check_user_exist, create_user
from app.user.models import User
from sqlalchemy.orm.session import Session
from app.utils.crud_util import get_model_or_404, ensure_unique_model, create_model, delete_model, list_model, get_model_by_field_first, update_model

from app.user_account import schemas, models


# =========[ Create ]=========

def create_uac_by_image(
    db: Session, 
    user_account: schemas.UserAccountByImage, 
    user_image: UploadFile, 
    current_user: UserSchema,
    autocommit: bool = True
):
    check_for_single_face(user_image)
    db_user: User = create_user(db, user_account.user, autocommit=False)
    if user_account.next_of_kin:
        db_next_of_kin: models.NextOfKin = create_model(db, models.NextOfKin, "Next Of Kin", user_account.next_of_kin,\
        autocommit=False)
        next_of_kin_uuid: Optional[str] = str(db_next_of_kin.uuid)
    else:
        next_of_kin_uuid = None

    try:
        user_image_url = upload_image_file_to_cloud(user_image, "USERS_IMAGE_BUCKET")
    except:
        raise HTTPException(500, "User image upload failed")
    
    to_create = schemas.UserAccountCreate(user_uuid=str(db_user.uuid), image=user_image_url, phone=user_account.phone,\
        address=user_account.address, gender=user_account.gender, birthdate=user_account.birthdate, \
        next_of_kin_uuid=next_of_kin_uuid, creator_uuid=str(current_user.uuid))
    
    db_user_account = create_model(db, models.UserAccount, "User Account", to_create, autocommit=False)
    if autocommit:
        db.commit()
        db.refresh(db_user_account)

    return db_user_account


def create_uac_by_nin(
    db: Session, 
    user_account: schemas.UserAccountByNIN, 
    user: UserSchema,
    autocommit: bool = True
):
    ensure_unique_model(db, models.UserAccount, {"nin": user_account.nin}, "User Account")
    db_nin_info: NIN = general_get_user_by_nin(db, user_account.nin)
    db_nin_info.phone = user_account.phone if user_account.phone else db_nin_info.phone
    check_user_exist(db, user_account.email)
    user_image_url = upload_remote_user_image(db_nin_info.image, "USERS_IMAGE_BUCKET")

    to_create = gen_user_from_nin(db_nin_info)
    to_create.email = user_account.email
    db_user: User = create_user(db, to_create, autocommit=False)

    if user_account.next_of_kin:
        nextofkin: models.NextOfKin = create_model(db, models.NextOfKin, "Next Of Kin", user_account.next_of_kin, autocommit=False)
        next_of_kin_uuid: Optional[str] = str(nextofkin.uuid)
    else:
        next_of_kin_uuid = None
    

    to_create = schemas.UserAccountCreate(user_uuid=str(db_user.uuid), nin=db_nin_info.nin, image=user_image_url, phone=db_nin_info.phone, \
        address=user_account.address, gender=db_nin_info.gender, \
        birthdate=datetime.strptime(db_nin_info.birthdate, "%d-%m-%Y").date(), \
        next_of_kin_uuid=next_of_kin_uuid, creator_uuid=str(user.uuid))

    db_user_account = create_model(db, models.UserAccount, "User Account", to_create, autocommit=False)
    if autocommit:
        db.commit()
        db.refresh(db_user_account)
    return db_user_account


def create_driver_by_image(
    db: Session, 
    driver: schemas.DriverCreateByImage, 
    driver_image: UploadFile, 
    guarantor_image: UploadFile, 
    user: UserSchema,
    bg_task: BackgroundTasks,
):
    verify_driver_creds(db, driver)
    db_uac = check_duplicate_driver_by_image(db, driver_image)
    if not db_uac:
        email = gen_email()

        user_to_create = UserIn(firstname=driver.firstname, lastname=driver.lastname, email=email, \
            password=gen_random_password())
        uac_to_create = schemas.UserAccountByImage(user=user_to_create, phone=driver.phone, address=driver.address, \
        gender=driver.gender, birthdate=driver.birthdate)
    
        db_uac = create_uac_by_image(db, uac_to_create, driver_image, user, autocommit=False)
    
    try:
        guarantor_image_url = upload_image_file_to_cloud(guarantor_image, "USERS_IMAGE_BUCKET")
    except:
        raise HTTPException(500, "Guarantor image upload failed")
    
    guarantor = schemas.GuarantorCreate(firstname=driver.guarantor_firstname, lastname=driver.guarantor_lastname, \
        middlename=driver.guarantor_middlename, phone=driver.guarantor_phone, address=driver.guarantor_address, \
        image=guarantor_image_url)
    
    db_guarantor: models.Guarantor = create_model(db, models.Guarantor, "Guarantor", guarantor, autocommit=False)
    
    guarantor_uuid = str(db_guarantor.uuid)
    expiry_date = date.today() + timedelta(days=365)
    unique_key = str(ulid.new())
    qr_code_image_url = get_driver_qr_url(unique_key, driver.association_number)

    to_create = schemas.DriverCreate(user_account_uuid=str(db_uac.uuid), complexion=driver.complexion, \
        expiry_date=expiry_date, \
        association_uuid=driver.association_uuid, association_number=driver.association_number, \
        vehicle_type_uuid=driver.vehicle_type_uuid, guarantor_uuid=guarantor_uuid, unique_key=unique_key, \
        qr_code_image=qr_code_image_url, creator_uuid=str(user.uuid))

    db_driver: models.Driver = create_model(db, models.Driver, "Driver", to_create)
    driver_act: models.UserAccount = db_driver.user_account
    bg_task.add_task(create_person, driver_act)
    bg_task.add_task(index_face_to_collection, driver_act.image, str(driver_act.uuid))
    return db_driver


def create_driver_by_nin(
    db: Session, 
    driver: schemas.DriverCreateByNIN, 
    guarantor_image: UploadFile, 
    user: UserSchema
):
    verify_driver_creds(db, driver)
    db_uac = check_duplicate_uac_by_nin(db, driver.nin)
    if not db_uac:
        email = gen_email()
        uac_to_create = schemas.UserAccountByNIN(nin=driver.nin, email=email, address=driver.address)
        db_uac = create_uac_by_nin(db, uac_to_create, user, autocommit=False)
    
    try:
        guarantor_image_url = upload_image_file_to_cloud(guarantor_image, "USERS_IMAGE_BUCKET")
    except:
        raise HTTPException(500, "Guarantor image upload failed")
    
    guarantor = schemas.GuarantorCreate(firstname=driver.guarantor_firstname, lastname=driver.guarantor_lastname, \
        middlename=driver.guarantor_middlename, phone=driver.guarantor_phone, address=driver.guarantor_address, \
        image=guarantor_image_url)
    
    db_guarantor: models.Guarantor = create_model(db, models.Guarantor, "Guarantor", guarantor, autocommit=False)
    guarantor_uuid = str(db_guarantor.uuid)

    expiry_date = date.today() + timedelta(days=365)
    unique_key = str(ulid.new())
    qr_code_image_url = get_driver_qr_url(unique_key, driver.association_number)

    to_create = schemas.DriverCreate(user_account_uuid=str(db_uac.uuid), complexion=driver.complexion, \
        expiry_date=expiry_date, \
        association_uuid=driver.association_uuid, association_number=driver.association_number, \
        vehicle_type_uuid=driver.vehicle_type_uuid, guarantor_uuid=guarantor_uuid, unique_key=unique_key, \
        qr_code_image=qr_code_image_url, creator_uuid=str(user.uuid))
    
    db_driver: models.Driver = create_model(db, models.Driver, "Driver", to_create)
    driver_act: models.UserAccount = db_driver.user_account
    index_face_to_collection(driver_act.image, str(driver_act.uuid))
    return db_driver


def issue_driver_id(
    db: Session, 
    issuance: IssuanceIn, 
    user: UserSchema
):
    db_driver: models.UserAccount = get_model_or_404(db, models.UserAccount, {"uuid": issuance.user_account_uuid}, \
        "Driver")
    issuance_to_create = IssuanceCreate(user_account_uuid=str(db_driver.uuid), item_name="DRIVER_ID_CARD", \
        issuer_uuid=str(user.uuid))
    return create_model(db, Issuance, "Driver ID Issuance", issuance_to_create)


# =========[ Read ]=========

def get_uac_by_uuid(
    db: Session, 
    uac_uuid: str
):
    db_uac: models.UserAccount = get_model_by_field_first(db, models.UserAccount, "uuid", "User Account", uac_uuid)
    if not db_uac:
        raise HTTPException(404, detail="User Account not found")
    return db_uac


def get_uac_by_image(
    db: Session,
    user_image: UploadFile
):
    try:
        uac_uuid = get_face_id(user_image, get_recognition_auth_token())
    except:
        raise HTTPException(404, detail="Face ID not found")
    
    return get_model_by_field_first(db, models.UserAccount, "uuid", "User Account", uac_uuid)


def get_driver_by_uuid(
    db: Session, 
    driver_uuid: str
):
    return get_model_by_field_first(db, models.Driver, "uuid", "Driver", driver_uuid)


def public_view_driver_info(db: Session, unique_key: str):
    db_driver: models.Driver = get_model_by_field_first(db, models.Driver, "unique_key", "Driver", unique_key)
    if not db_driver:
        raise HTTPException(404, detail="Driver not found")
    
    license_validity = LicenseValidity.valid if db_driver.expiry_date >= date.today() else LicenseValidity.expired
    return {"license_validity": license_validity, "driver_info": db_driver}

# =========[ Update ]=========

def uac_image_update(
    db: Session, 
    user_image: UploadFile, 
    uac_uuid: str,
    autocommit = True,
):
    db_uac: models.UserAccount = get_model_or_404(db, models.UserAccount, {"uuid": uac_uuid}, "User Account")
    try:
        user_image_url = upload_image_file_to_cloud(user_image, "USERS_IMAGE_BUCKET")
    except:
        raise HTTPException(500, "User image upload failed")
    
    db_uac.image = user_image_url
    if autocommit:
        db.commit()
        db.refresh(db_uac)
    
    return db_uac


def update_driver(
    db: Session,
    driver: schemas.DriverUpdate,
    driver_id: str
):
    db_driver: models.Driver = get_model_by_field_first(db, models.Driver, "uuid", "Driver", driver_id)
    if not db_driver:
        raise HTTPException(404, detail="Driver not found")
    
    to_update = driver.dict(exclude_unset=True)
    
    db_driver_uac: models.UserAccount = db_driver.user_account
    db_user: User = db_driver_uac.user

    db_driver_schema = schemas.DriverOut.from_orm(db_driver)
    driver_dict = db_driver_schema.dict()
    driver_dict.update(to_update)
    to_update_driver = schemas.DriverUpdate(**driver_dict)

    db_driver_uac_schema = schemas.UserAccountOut.from_orm(db_driver_uac)
    driver_uac_dict = db_driver_uac_schema.dict()
    driver_uac_dict.update(to_update)
    to_update_driver_uac = schemas.UserAccountUpdate(**driver_uac_dict)

    db_user_schema = UserSchema.from_orm(db_user)
    db_user_dict = db_user_schema.dict()
    db_user_dict.update(to_update)
    to_update_user = UserUpdate(**db_user_dict)

    update_model(db, models.Driver, to_update_driver, "Driver", {"uuid": driver_id}, autocommit=False)
    update_model(db, models.UserAccount, to_update_driver_uac, "User Account", {"uuid": str(db_driver_uac.uuid)}, autocommit=False)
    update_model(db, User, to_update_user, "User", {"uuid": str(db_user.uuid)})
    return db_driver


def update_driver_image(db: Session, driver_image: UploadFile, driver_uuid: str):
    db_driver: models.Driver = get_model_or_404(db, models.Driver, {"uuid": driver_uuid}, "Driver")
    db_driver_uac: models.UserAccount = db_driver.user_account
    db_uac = uac_image_update(db, driver_image, str(db_driver_uac.uuid))
    db.refresh(db_driver)
    index_face_to_collection(db_uac.image, str(db_uac.uuid))
    return db_driver


# =========[ List ]=========

def list_all_uac(
    db: Session, 
    filter: schemas.UserAccountFilter, 
    skip: int, 
    limit: int
):
    fields = {"nin": filter.nin, "birthdate": filter.birthdate}
    join_fields = {
        User: {"firstname": filter.firstname, "lastname": filter.lastname, \
            "middlename": filter.middlename, "email": filter.email, "phone": filter.phone}
    }

    return list_model(db, models.UserAccount, fields, "User Account", \
        limit=limit, skip=skip, count_by_column="uuid", join_conditions=join_fields)


def list_driver(
    db: Session, 
    filter: schemas.DriverFilter,
    skip: int, 
    limit: int
):
    fields = {"association_number": filter.association_number, "association_uuid": filter.association_uuid, \
        "vehicle_type_uuid": filter.vehicle_type_uuid, \
        "complexion": filter.complexion}
    
    join_fields = {
        models.UserAccount: {"phone": filter.phone, "nin": filter.nin, "gender": filter.gender}
    }

    return list_model(db, models.Driver, fields, "Driver", \
        limit=limit, skip=skip, join_conditions=join_fields)


def list_own_driver(
    db: Session, 
    filter: schemas.DriverFilter,
    skip: int, 
    limit: int,
    user: UserSchema
):
    fields = {"association_number": filter.association_number, "association_uuid": filter.association_uuid, \
        "vehicle_type_uuid": filter.vehicle_type_uuid, \
        "complexion": filter.complexion, "creator_uuid": str(user.uuid)}
    
    join_fields = {
        models.UserAccount: {"phone": filter.phone, "nin": filter.nin, "gender": filter.gender}
    }

    return list_model(db, models.Driver, fields, "Driver", \
        limit=limit, skip=skip, join_conditions=join_fields)


# =========[ Delete ]=========

def delete_driver(db: Session, driver_uuid: str):
    return delete_model(db, models.Driver, "Driver", {"uuid": driver_uuid})

# =========[ Helpers ]=========

def upload_remote_user_image(image_url: str, bucket_var_name: str):
    filename = f"{str(ulid.new())}.png"

    image_url = upload_remote_image_to_cloud(image_url, filename, bucket_var_name)
    if not image_url:
        raise HTTPException(403, detail="Could not upload user image to cloud")
    
    return image_url


def check_duplicate_driver_by_image(db: Session, driver_image: UploadFile):
    try:
        db_uac: models.UserAccount = get_uac_by_image(db, driver_image)
        if db_uac and db_uac.driver:
            raise HTTPException(409)
        if db_uac and db_uac.vehicles:
            # if this user already exists as vehicle owner, return the user account
            return db_uac
    except HTTPException as e:
        if e.status_code == 409:
            raise HTTPException(409, detail="Driver already exists, duplicate driver not allowed")
        


def verify_driver_creds(db: Session, driver: Union[schemas.DriverCreateByImage, schemas.DriverCreateByNIN]):
    ensure_unique_model(db, models.Driver, {"association_number": driver.association_number}, "Association Number")


def get_driver_qr_url(unique_key: str, association_number: str = "") -> str:
    qr_data = f"{getenv('DOMAIN', '')}{getenv('DRIVER_QR_PATH', '')}{unique_key}"
    qr_filename = f"{str(ulid.new())}.png"
    qr_upload_status = create_and_upload_qr_cloud(qr_data, "VEHICLE_QR_BUCKET", qr_filename, association_number)
    if not qr_upload_status:
        raise HTTPException(500, detail="Failed to create and upload driver qr code")
    return f"{getenv('CLOUD_STORAGE_PATH')}{getenv('VEHICLE_QR_BUCKET')}/{qr_filename}"


def check_duplicate_uac_by_nin(db: Session, nin: str):
    try:
        db_uac: models.UserAccount = get_model_by_field_first(db, models.UserAccount, "nin", "User Account", nin)
        if db_uac and db_uac.driver:
            raise HTTPException(409)
        
        if db_uac:
            # uac with this NIN already exists
            return db_uac
        
    except HTTPException as e:
        if e.status_code == 409:
            raise HTTPException(409, detail="Driver already exists, duplicate driver not allowed")

