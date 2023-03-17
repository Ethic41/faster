#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-19 21:33:57
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from typing import Any
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Production Settings"""
    app_name: str = "Faster Template"
    environment: str = ""
    
    # database settings
    postgres_user: str
    postgres_password: str
    postgres_db: str
    test_database_name: str
    database_private_address: str
    database_public_address: str
    database_port: str
    database_private_url: str = ""
    database_public_url: str = ""
    database_test_url: str = ""
    database_pool_size: int = 50
    database_max_overflow: int = 85

    # jwt settings
    jwt_secret_key: str
    jwt_algorithm: str
    token_life_span: int
    token_long_life_span: int

    # url
    token_url: str
    frontend_url: str

    # email
    source_email: str
    sendgrid_api_key: str

    # cloud
    cloud_bucket_name: str
    cloud_storage_url: str

    # cors
    cors_origins: list[str] = []

    @validator("database_private_url")
    def _val_private_db_url(cls, v: str, values: dict[str, Any]) -> str:

        return f"postgresql://{values['postgres_user']}:{values['postgres_password']}@{values['database_private_address']}:{values['database_port']}/{values['postgres_db']}" # noqa E501
    

    @validator("database_public_url")
    def _val_public_db_url(cls, v: str, values: dict[str, Any]) -> str:

        return f"postgresql://{values['postgres_user']}:{values['postgres_password']}@{values['database_public_address']}:{values['database_port']}/{values['postgres_db']}" # noqa E501
    
    
    @validator("database_test_url")
    def _val_test_db_url(cls, v: str, values: dict[str, Any]) -> str:

        return f"postgresql://{values['postgres_user']}:{values['postgres_password']}@{values['database_public_address']}:{values['database_port']}/{values['test_database_name']}" # noqa E501
    

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
