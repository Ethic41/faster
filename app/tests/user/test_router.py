#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-30 07:10:12
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import EmailStr
from app.tests.utils.utils import gen_user
from app.user import models, schemas, cruds
from app.utils.crud_util import CrudUtil
from app.utils.misc import gen_email, gen_random_password


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


def test_login_with_wrong_email(
    client: TestClient, 
) -> None:

    response = client.post(
        "/auth/token",
        json=schemas.Login(
            email=gen_email(),
            password=gen_random_password(),
        ).dict()
    )

    res_payload = response.json()

    assert response.status_code == 400
    assert "detail" in res_payload
    assert res_payload["detail"] == "Email and password do not match"


def test_login_with_inactive_user(
    client: TestClient, 
    inactive_admin_user: models.User,
    create_account_mailbox: Path,
) -> None:

    password = create_account_mailbox.read_text().strip()
    response = client.post(
        "/auth/token",
        json=schemas.Login(
            email=inactive_admin_user.email,
            password=password,
        ).dict()
    )

    res_payload = response.json()

    assert response.status_code == 400
    assert "detail" in res_payload
    assert res_payload["detail"] == "User is not active"


def test_request_password_reset(
    client: TestClient, 
    admin_user: models.User,
    password_reset_mailbox: Path,
) -> None:

    response = client.post(
        "/auth/forgot-password",
        params={"email": admin_user.email},
    )

    res_payload = response.json()

    token = password_reset_mailbox.read_text().strip()

    assert "reset-password" in token
    assert response.status_code == 200
    assert "detail" in res_payload
    assert res_payload["detail"] == "We've sent a password reset link to your mail"


def test_request_password_reset_wrong_email(
    client: TestClient, 
) -> None:

    response = client.post(
        "/auth/forgot-password",
        params={"email": gen_email()},
    )

    res_payload = response.json()

    assert response.status_code == 200
    assert "detail" in res_payload
    assert res_payload["detail"] == "We've sent a password reset link to your mail"


def test_reset_password(
    client: TestClient,
    crud_util: CrudUtil,
    admin_user: models.User,
    password_reset_mailbox: Path,
) -> None:

    
    cruds.request_password_reset(
        crud_util,
        EmailStr(admin_user.email),
    )

    token = password_reset_mailbox.read_text().strip().split("/")[-1]

    response = client.post(
        f"/auth/reset-password/{token}"
    )

    res_payload = response.json()
    print(token)
    assert response.status_code == 200
    assert "detail" in res_payload
    assert "Password reset successful" in res_payload["detail"]


def test_reset_password_wrong_token(
    client: TestClient,
) -> None:

    response = client.post(
        f"/auth/reset-password/{gen_random_password()}"
    )

    res_payload = response.json()

    assert response.status_code == 400
    assert "detail" in res_payload
    assert "Invalid token" in res_payload["detail"]


def test_create_admin_user(
    client: TestClient,
    su_token_headers: dict[str, str],
    crud_util: CrudUtil,
) -> None:

    user_data = gen_user().dict()

    response = client.post(
        "/users",
        json=user_data,
        headers=su_token_headers,
    )

    res_payload = response.json()

    assert response.status_code == 201
    assert "id" in res_payload
    assert res_payload["email"] == user_data["email"]
    assert res_payload["is_active"] is True


def test_create_admin_user_with_existing_email(
    client: TestClient,
    su_token_headers: dict[str, str],
    admin_user: models.User,
) -> None:

    user_data = gen_user().dict()

    user_data["email"] = admin_user.email

    response = client.post(
        "/users",
        json=user_data,
        headers=su_token_headers,
    )

    res_payload = response.json()

    assert response.status_code == 409
    assert "detail" in res_payload
    assert res_payload["detail"] == "User already exists"


def test_create_admin_user_invalid_token(
    client: TestClient,
) -> None:

    user_data = gen_user().dict()

    response = client.post(
        "/users",
        json=user_data,
        headers={"Authorization": f"Bearer {gen_random_password()}"},
    )

    res_payload = response.json()

    assert response.status_code == 401
    assert "detail" in res_payload
    assert res_payload["detail"] == "Could not validate credentials"