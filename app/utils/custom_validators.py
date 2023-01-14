#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-06-22 06:52:50
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from datetime import date
from typing import Optional
from fastapi.exceptions import HTTPException
from pydantic import validator

# convert from naira to kobo, as all
# values in database should be in kobo
def currency_in(amount: float) -> Optional[float]:
    if amount is not None: return amount * 100
    return None


# convert from kobo back to naira
def currency_out(amount: float) -> Optional[float]:
    if amount is not None: return amount / 100
    return None


def currency_in_val(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(currency_in)


def currency_out_val(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(currency_out)


def make_uppercase(value: str) -> Optional[str]:
    if value is not None: return value.upper()
    return None


def make_lowercase(value: str) -> Optional[str]:
    if value is not None: return value.lower()
    return None


def check_is_18_above(value: date):
    if not value:
        return None
    
    if date.today().year - value.year < 18:
        raise HTTPException(403, detail="Age must 18 years or above to register")
    
    return value


def uppercased(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(make_uppercase)


def lowercased(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(make_lowercase)


def checkbirthdate(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(check_is_18_above)


def clean_string(value: str) -> Optional[str]:
    if value is not None: return value.replace(' ', '').replace('-', '').replace('_', '').replace('/', '').replace('\\','')
    return None


def cleaned(field: str) -> classmethod:
    return validator(field, allow_reuse=True)(clean_string)

