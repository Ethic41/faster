#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-19 21:33:57
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from typing import Any
from pydantic import BaseSettings, validator
from enum import Enum


class EnvType(str, Enum):
    local: str = "LOCAL"
    testing: str = "TESTING"
    staging: str = "STAGING"
    production: str = "PRODUCTION"


class Settings(BaseSettings):
    """Production Settings"""
    app_name: str = "Faster Template"
    environment: EnvType
    
    # database settings
    database_username: str
    database_password: str
    database_name: str
    database_private_address: str
    database_public_address: str
    database_port: str
    database_url: str = ""
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

    @validator("database_url")
    def _val_db_url(cls, v: str, values: dict[str, Any]) -> str:

        return f"postgres://{values['database_username']}:{values['database_password']}@{values['database_private_address']}:{values['database_port']}/{values['database_name']}" # noqa E501
    

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        


class TestSettings(BaseSettings):
    pass

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
test_settings = TestSettings()
