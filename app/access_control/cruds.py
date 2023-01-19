#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-17 10:44:39
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from typing import Any
from app.access_control import models, schemas
from app.utils.crud_util import CrudUtil


def create_permission(
    cu: CrudUtil,
    perm_data: schemas.PermissionCreate
) -> models.Permission:

    cu.ensure_unique_model(models.Permission, {"name": perm_data.name})
    permission: models.Permission = cu.create_model(models.Permission, perm_data)
    return permission


def get_perm_by_name(
    cu: CrudUtil, 
    name: str
) -> models.Permission:

    permission: models.Permission = cu.get_model_or_404(
        models.Permission, 
        {"name": name}
    )
    return permission


def update_permission(
    cu: CrudUtil,
    name: str,
    update_data: schemas.PermissionUpdate,
) -> models.Permission:

    permission: models.Permission = cu.update_model(
        model_to_update=models.Permission,
        update=update_data,
        update_conditions={"name": name}
    )

    return permission


def list_permission(
    cu: CrudUtil,
    skip: int,
    limit: int,
) -> schemas.PermissionList:
    
    permissions: dict[str, Any] = cu.list_model(
        model_to_list=models.Permission,
        skip=skip,
        limit=limit
    )

    return schemas.PermissionList(**permissions)


def delete_permission(
    cu: CrudUtil,
    name: str,
) -> dict[str, Any]:
    return cu.delete_model(
        model_to_delete=models.Permission,
        delete_conditions={"name": name}
    )


def create_role(
    cu: CrudUtil, 
    role_data: schemas.RoleCreate
) -> models.Role:

    cu.ensure_unique_model(
        model_to_check=models.Role, 
        unique_condition={"name": role_data.name}
    )

    role: models.Role = cu.create_model(
        model_to_create=models.Role, 
        create=role_data
    )

    return role


def get_role_by_name(
    cu: CrudUtil, 
    name: str,
) -> models.Role:

    role: models.Role = cu.get_model_or_404(
        model_to_get=models.Role,
        model_conditions={"name": name}
    )
    return role


def update_role(
    cu: CrudUtil,
    name: str,
    update_data: schemas.RoleUpdate,
) -> models.Role:

    role: models.Role = cu.update_model(
        model_to_update=models.Role,
        update=update_data,
        update_conditions={"name": name},
        autocommit=False if update_data.permissions else True,
    )

    if update_data.permissions:
        for perm_name in update_data.permissions:
            role.permissions.append(
                get_perm_by_name(cu=cu, name=perm_name)
            )
    
    cu.db.commit()
    cu.db.refresh(role)

    return role


def list_role(cu: CrudUtil, skip: int, limit: int) -> schemas.RoleList:
    roles: dict[str, Any] = cu.list_model(
        model_to_list=models.Role,
        skip=skip,
        limit=limit
    )

    return schemas.RoleList(**roles)


def delete_role(cu: CrudUtil, name: str) -> dict[str, Any]:
    return cu.delete_model(
        model_to_delete=models.Role,
        delete_conditions={"name": name}
    )


def create_group(cu: CrudUtil, group_data: schemas.GroupCreate) -> models.Group:

    cu.ensure_unique_model(
        model_to_check=models.Group, 
        unique_condition={"name": group_data.name}
    )

    group: models.Group = cu.create_model( 
        model_to_create=models.Group, 
        create=group_data
    )

    return group


def get_group_by_name(cu: CrudUtil, name: str) -> models.Group:
    group: models.Group = cu.get_model_or_404(
        model_to_get=models.Group,
        model_conditions={"name": name}
    )
    return group


def update_group(
    cu: CrudUtil,
    name: str,
    update_data: schemas.GroupUpdate,
) -> models.Group:

    group: models.Group = cu.update_model(
        model_to_update=models.Group,
        update=update_data,
        update_conditions={"name": name},
        autocommit=False if update_data.roles else True,
    )

    if update_data.roles:
        for role_name in update_data.roles:
            group.roles.append(
                get_role_by_name(cu=cu, name=role_name)
            )
    
    cu.db.commit()
    cu.db.refresh(group)

    return group


def list_group(
    cu: CrudUtil,
    skip: int,
    limit: int,
) -> schemas.GroupList:
    
    groups: dict[str, Any] = cu.list_model(
        model_to_list=models.Group,
        skip=skip,
        limit=limit
    )

    return schemas.GroupList(**groups)


def delete_group(
    cu: CrudUtil,
    name: str,
) -> dict[str, Any]:
    return cu.delete_model(
        model_to_delete=models.Group,
        delete_conditions={"name": name}
    )

