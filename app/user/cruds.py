from typing import Dict
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks

from app.user import schemas, models
from app.utils.crud_util import CrudUtil
from app.utils.mail import send_change_password_mail, send_account_create_mail
from app.utils.misc import gen_random_password
from app.utils.user import get_password_hash, verify_password


def create_user(
    cu: CrudUtil,
    user_data: schemas.UserIn,
    autocommit: bool = True,
    can_login: bool = False
) -> models.User:

    user_to_create = schemas.UserCreate(
        **user_data.dict(),
        password_hash="",
        can_login=can_login,
    )

    cu.ensure_unique_model(
        model_to_check=models.User, 
        unique_condition={"email": user_data.email}
    )

    user: models.User = cu.create_model(
        model_to_create=models.User,
        create=user_to_create,
        autocommit=autocommit
    )
    
    if can_login:
        send_account_create_mail(
            str(user.email), 
            user_to_create.password, 
            user.firstname
        )
    
    return user


def get_user_by_email(
    cu: CrudUtil, 
    email: EmailStr
) -> models.User:
    user: models.User = cu.get_model_or_404(
        model_to_get=models.User,
        model_conditions={"email": email}
    )

    return user


def authenticate_user(
    cu: CrudUtil,
    email: EmailStr, 
    password: str, 
):
    try:
        user: models.User = get_user_by_email(cu, email)
    except HTTPException as e:
        if e.status_code == 404:
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

