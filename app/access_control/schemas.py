#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-17 10:51:44
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from pydantic import BaseModel
from app.mixins.commons import ListBase

from app.mixins.schemas import BaseUACSchemaMixin
from app.utils.custom_validators import lowercased



class PermissionCreate(BaseModel):
    name: str
    description: str | None

    _val_name = lowercased("name")


class PermissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    _val_name = lowercased("name")


class PermissionSchema(BaseUACSchemaMixin):
    pass


class PermissionList(ListBase):
    model_list: list[PermissionSchema]


class RoleCreate(BaseModel):
    name: str
    description: str | None

    _val_name = lowercased("name")


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: list[str] | None

    _val_name = lowercased("name")


class RemoveRolePermission(BaseModel):
    permissions: list[str]


class RoleSchema(BaseUACSchemaMixin):
    permissions: list[PermissionSchema]


class RoleList(ListBase):
    model_list: list[RoleSchema]


class GroupCreate(BaseModel):
    name: str
    description: str | None

    _val_name = lowercased("name")


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    roles: list[str] | None

    _val_name = lowercased("name")


class RemoveGroupRole(BaseModel):
    roles: list[str]


class GroupSchema(BaseUACSchemaMixin):
    roles: list[RoleSchema]


class GroupList(ListBase):
    model_list: list[GroupSchema]


class GroupOutSchema(BaseUACSchemaMixin):
    pass

