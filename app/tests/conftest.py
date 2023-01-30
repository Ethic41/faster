#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-25 11:56:44
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator, Any
from pytest import TempPathFactory
import pytest

from app.config.database import TestSessionLocal, Base, test_engine
from app.tests.utils.utils import gen_user
from app.user import cruds as user_cruds, models as user_models, schemas as user_schemas
from app.utils.crud_util import CrudUtil
from app.main import app


Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="session")
def monkeymodule() -> Any:
    with pytest.MonkeyPatch.context() as m:
        yield m


@pytest.fixture(scope="session")
def db() -> Generator[Session, Any, Any]:
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def crud_util(db: Session) -> CrudUtil:
    return CrudUtil(db)


@pytest.fixture(scope="module")
def client() -> Generator[Any, Any, Any]:
    with TestClient(app) as c:
        yield c




@pytest.fixture(scope="module")
def mock_account_create_mail(
    monkeymodule: Any, tmp_path_factory: TempPathFactory
) -> None:
    def mock_send_account_create_mail(*args: Any, **kwargs: Any) -> None:
        tmp_dir = tmp_path_factory.getbasetemp()
        tmp_dir = tmp_dir / "mailbox"
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / "account_create_mail.txt"
        tmp_file.write_text(args[1])
    
    monkeymodule.setattr(
        "app.user.cruds.send_account_create_mail", mock_send_account_create_mail,
    )


@pytest.fixture(scope="module")
def mock_password_reset_mail(
    monkeymodule: Any, tmp_path_factory: TempPathFactory
) -> None:
    def mock_send_password_reset_mail(*args: Any, **kwargs: Any) -> None:
        tmp_dir = tmp_path_factory.getbasetemp()
        tmp_dir = tmp_dir / "mailbox"
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / "password_reset_mail.txt"
        tmp_file.write_text(args[1])
    
    monkeymodule.setattr(
        "app.user.cruds.send_password_reset_link_mail", mock_send_password_reset_mail,
    )


@pytest.fixture(scope="module")
def mock_password_change_mail(
    monkeymodule: Any, tmp_path_factory: TempPathFactory
) -> None:
    def mock_send_password_change_mail(*args: Any, **kwargs: Any) -> None:
        tmp_dir = tmp_path_factory.getbasetemp()
        tmp_dir = tmp_dir / "mailbox"
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / "password_change_mail.txt"
        tmp_file.write_text(args[1])
    
    monkeymodule.setattr(
        "app.user.cruds.send_change_password_mail", mock_send_password_change_mail,
    )


@pytest.fixture(scope="module")
def create_account_mailbox(
    mock_account_create_mail: Any,
    tmp_path_factory: TempPathFactory
) -> Path:
    tmp_dir = tmp_path_factory.getbasetemp()
    mail_file = tmp_dir / "mailbox" / "account_create_mail.txt"
    return mail_file


@pytest.fixture(scope="module")
def password_reset_mailbox(
    mock_password_reset_mail: Any,
    tmp_path_factory: TempPathFactory
) -> Path:
    tmp_dir = tmp_path_factory.getbasetemp()
    mail_file = tmp_dir / "mailbox" / "password_reset_mail.txt"
    return mail_file


@pytest.fixture(scope="module")
def password_change_mailbox(
    mock_password_change_mail: Any,
    tmp_path_factory: TempPathFactory
) -> Path:
    tmp_dir = tmp_path_factory.getbasetemp()
    mail_file = tmp_dir / "mailbox" / "password_change_mail.txt"
    return mail_file


@pytest.fixture(scope="function")
def user(crud_util: CrudUtil) -> Any:
    user_data: user_schemas.UserIn = gen_user()
    user = user_cruds.create_user(
        crud_util,
        user_data,
    )
    return user


@pytest.fixture(scope="function")
def admin_user(crud_util: CrudUtil, mock_account_create_mail: Any) -> Any:
    user_data: user_schemas.UserIn = gen_user()
    user = user_cruds.create_user(
        crud_util,
        user_data,
        is_admin=True
    )
    return user


@pytest.fixture(scope="function")
def admin_users(
    crud_util: CrudUtil, 
    mock_account_create_mail: Any
) -> list[user_models.User]:
    users = []
    for i in range(5):
        user_data: user_schemas.UserIn = gen_user()
        user = user_cruds.create_user(
            crud_util,
            user_data,
            is_admin=True
        )
        users.append(user)
    return users

