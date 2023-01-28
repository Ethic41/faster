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
from app.utils.crud_util import CrudUtil
from app.main import app


Base.metadata.create_all(bind=test_engine)


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


@pytest.fixture(scope="session")
def monkeymodule() -> Any:
    with pytest.MonkeyPatch.context() as m:
        yield m


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
def create_account_mailbox(
    mock_account_create_mail: Any,
    tmp_path_factory: TempPathFactory
) -> Path:
    tmp_dir = tmp_path_factory.getbasetemp()
    mail_file = tmp_dir / "mailbox" / "account_create_mail.txt"
    return mail_file

