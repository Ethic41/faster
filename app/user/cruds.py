from os import getenv
from typing import Any
from pydantic import EmailStr
from fastapi import HTTPException, BackgroundTasks
from jose import JWSError, jws

from app.user import schemas, models
from app.utils.crud_util import CrudUtil
from app.utils.mail import (
    send_change_password_mail, 
    send_account_create_mail,
    send_password_reset_link_mail,
)
from app.utils.misc import gen_random_password
from app.utils.user import get_password_hash, verify_password


def create_user(
    cu: CrudUtil,
    user_data: schemas.UserIn,
    autocommit: bool = True,
    is_admin: bool = False
) -> models.User:

    # password and hash generated
    # in class using validators
    user_to_create = schemas.UserCreate(
        **user_data.dict(),
        password_hash="",
        is_admin=is_admin,
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
    
    if is_admin:
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


def get_user_by_uuid(
    cu: CrudUtil,
    uuid: str,
) -> models.User:

    user: models.User = cu.get_model_or_404(
        model_to_get=models.User,
        model_conditions={"uuid": uuid}
    )
    return user


def update_user(
    cu: CrudUtil,
    uuid: str,
    user_data: schemas.UserUpdate,
) -> models.User:
    
    user: models.User = cu.update_model(
        model_to_update=models.User,
        update=user_data,
        update_conditions={"uuid": uuid},
    )

    return user


def delete_user(
    cu: CrudUtil, 
    uuid: str
) -> dict[str, Any]:

    return cu.delete_model(
        model_to_delete=models.User,
        delete_conditions={"uuid": uuid}
    )


def authenticate_user(
    cu: CrudUtil,
    email: EmailStr, 
    password: str, 
) -> schemas.UserSchema:
    try:
        user: models.User = get_user_by_email(cu, email)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail='Email and password do not match'
            )
        raise e
    
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


def request_password_reset(
    cu: CrudUtil,
    email: EmailStr,
) -> dict[str, Any]:

    sent_email = (
        "We've sent a password reset link to your mail"
    )

    try:
        user = get_user_by_email(cu, email)
        signed_token = jws.sign(
            str(user.email).encode(), getenv("JWT_SECRET_KEY"), algorithm="HS256"
        )

        reset_link = f"{getenv('FRONTEND_URL')}/reset-password/{signed_token}"
        send_password_reset_link_mail(str(user.email), reset_link)
        return {'detail': sent_email}
        
    except HTTPException:
        return {'detail': sent_email}


def reset_password(
    cu: CrudUtil,
    token: str,
) -> dict[str, Any]:

    try:
        token_data = jws.verify(token, getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        user = get_user_by_email(cu, token_data.decode())
        new_password = gen_random_password()
        new_password_hash = get_password_hash(new_password)
        user.password_hash = new_password_hash
        cu.db.commit()
        send_change_password_mail(str(user.email), new_password)
        return {
            "detail": "Password reset successful. " 
            f"Your new password is {new_password}. "
            "It has also been sent to your mail"
        }
        
    except JWSError:
        raise HTTPException(
            status_code=400,
            detail='Invalid token'
        )
    
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail='Invalid token'
            )
        raise e


def list_admin_users(
    cu: CrudUtil, 
    filter_: schemas.AdminUserFilter, 
    skip: int = 0,
    limit: int = 100
) -> schemas.UserList:
    conditions = {
        "firstname": filter_.firstname, 
        "lastname": filter_.lastname, 
        "email": filter_.email,
        "middlename": filter_.middlename, 
        "is_admin": True, 
        "is_active": filter_.is_active
    }
    
    db_result: dict[str, Any] = cu.list_model(
        model_to_list=models.User,
        list_conditions=conditions,
        skip=skip, 
        limit=limit,
    )

    if filter_.user_group_name:
        def filter_user_group(user: models.User) -> bool | Any:
            if user.groups:
                return user.groups[0].name == filter_.user_group_name
            
            return False

        db_result["model_list"] = list(
            filter(filter_user_group, db_result["model_list"])
        )
        return schemas.UserList(**db_result)

    return schemas.UserList(**db_result)


def change_admin_password(
    cu: CrudUtil,
    user_uuid: str,
    bg_task: BackgroundTasks
) -> schemas.PasswordChangeOut:
    db_user: models.User = cu.get_model_or_404(
        model_to_get=models.User, 
        model_conditions={"uuid": user_uuid}
    )
    password = gen_random_password()
    hashed_password = get_password_hash(password)
    
    db_user.password_hash = hashed_password
    cu.db.commit()
    bg_task.add_task(send_change_password_mail, db_user.email, password)
    return schemas.PasswordChangeOut(password=password)

