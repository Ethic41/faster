#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-25 11:56:44
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.config.database import TestSessionLocal
from typing import Generator, Any
import pytest

from app.main import app


@pytest.fixture(scope="session")
def db() -> Generator[Session, Any, Any]:
    yield TestSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator[Any, Any, Any]:
    with TestClient(app) as c:
        yield c

