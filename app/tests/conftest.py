#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-25 11:56:44
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator, Any
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

