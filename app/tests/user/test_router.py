#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-30 07:10:12
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from pathlib import Path
from fastapi.testclient import TestClient
from app.user import models, schemas
from app.utils.misc import gen_random_password


def test_login(
    client: TestClient, 
    admin_user: models.User,
    create_account_mailbox: Path,
) -> None:
    
    password = create_account_mailbox.read_text().strip()

    response = client.post(
        "/auth/token",
        json=schemas.Login(
            email=admin_user.email,
            password=password,
        ).dict()
    )
    res_payload = response.json()

    assert response.status_code == 200
    assert "access_token" in res_payload
    assert "permissions" in res_payload


def test_login_with_wrong_password(
    client: TestClient, 
    admin_user: models.User,
) -> None:

    response = client.post(
        "/auth/token",
        json=schemas.Login(
            email=admin_user.email,
            password=gen_random_password(),
        ).dict()
    )
    res_payload = response.json()

    assert response.status_code == 400
    assert "detail" in res_payload
    assert res_payload["detail"] == "Email and password do not match"


