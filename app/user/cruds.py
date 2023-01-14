from typing import Dict
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks

from app.user import schemas, models
from app.utils.mail import send_change_password_mail, send_account_create_mail
from app.utils.misc import gen_random_password
from app.utils.user import get_password_hash, verify_password
from app.utils.crud_util import create_model, get_model_by_field_first, list_model


def create_user(
    db: Session, 
    user_data: schemas.UserIn, 
    autocommit=True, 
    can_login=False
):
    user_to_create = schemas.UserCreate(
        **user_data.dict(),
        password_hash="",
        can_login=can_login,
    )

    user: models.User = create_model(
        db, 
        models.User, 
        user_to_create
    )
    
    if can_login:
        send_account_create_mail(str(user.email), unhashed_password, user.firstname)
    return user


def get_user_by_email(db: Session, email: EmailStr):
    return db.query(models.User).filter(models.User.email == email).first()


def check_user_exist(db: Session, email: EmailStr):
    db_user = get_user_by_email(db=db, email=email)
    if db_user:
        raise HTTPException(403, detail="User already exists")


def get_user_by_uuid(db: Session, uuid: str):
    return db.query(models.User).filter(models.User.uuid == str(uuid)).first()


def get_password_reset_by_uuid(db: Session, uuid: str):
    return db.query(models.PasswordReset). \
        filter(models.PasswordReset.uuid == uuid). \
        first()


def authenticate_user(email: EmailStr, password: str, dba: Session):
    user = get_user_by_email(db=dba, email=email)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Email and password do not match'
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail='User is not active'
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail='Email and password do not match'
        )
    return schemas.UserSchema.from_orm(user) 


def list_system_users(
    db: Session, 
    filter_: schemas.SystemUserFilter, 
    skip: int = 0, 
    limit: int = 100
):
    fields = {"firstname": filter_.firstname, "lastname": filter_.lastname, "email": filter_.email, \
        "middlename": filter_.middlename, "is_system_user": True, "is_active": filter_.is_active}
    
    db_result: Dict = list_model(db, models.User, fields, "User", skip=skip, limit=limit, \
        order_by_column="id")

    if filter_.user_group_name:
        def filter_user_group(user: models.User):
            if user.groups:
                return user.groups[0].name == filter_.user_group_name
        
        db_result["result"] = list(filter(filter_user_group, db_result["result"]))
        return db_result
    
    if filter_.has_wallet is not None:
        def filter_has_wallet(user: models.User):
            return get_model_by_field_first(db, Wallet, "owner_uuid", "Wallet", user.uuid) is not None

        
        def filter_has_no_wallet(user: models.User):
            return get_model_by_field_first(db, Wallet, "owner_uuid", "Wallet", user.uuid) is None

        if filter_.has_wallet:
            db_result["result"] = list(filter(filter_has_wallet, db_result["result"]))
        else:
            db_result["result"] = list(filter(filter_has_no_wallet, db_result["result"]))
        
        return db_result

    return db_result


def change_system_user_password(db: Session, user_uuid: str, bg_task: BackgroundTasks):
    db_user: models.User = get_model_by_field_first(db, models.User, "uuid", "User", user_uuid)
    if not db_user:
        raise HTTPException(404, detail="User not found")
    password = gen_random_password()
    hashed_password = get_password_hash(password)
    
    db_user.password_hash = hashed_password
    db.commit()
    bg_task.add_task(send_change_password_mail, db_user.email, password)
    return schemas.PasswordChangeOut(password=password)

