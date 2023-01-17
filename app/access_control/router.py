#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-17 11:05:42
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from typing import Any
from fastapi import APIRouter, Depends

import app.dependencies.dependencies as deps
from app.access_control import cruds, schemas
from app.utils.crud_util import CrudUtil



perms_router = APIRouter(
    prefix='/permissions',
    tags=['Permissions']
)
roles_router = APIRouter(
    prefix='/roles',
    tags=['Roles']
)
groups_router = APIRouter(
    prefix='/groups',
    tags=['Groups']
)


# ================ Permissions ================
@perms_router.post(
    '',
    status_code=201,
    dependencies=[Depends(deps.HasPermission(['permission:create']))]
)
async def create_permission(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    perm_data: schemas.PermissionCreate,
) -> schemas.PermissionSchema:

    return cruds.create_permission(cu=cu, perm_data=perm_data)


@perms_router.get(
    '',
    dependencies=[Depends(deps.HasPermission(['permission:list']))]
)
def list_permissions(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    skip: int = 0,
    limit: int = 100,
) -> schemas.PermissionList:

    return cruds.list_permission(cu=cu, skip=skip, limit=limit)


@perms_router.get(
    '/{perm_name}',
    dependencies=[Depends(deps.HasPermission(['permission:read']))]
)
def permission_detail(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    perm_name: str, 
) -> schemas.PermissionSchema:

    permission = cruds.get_perm_by_name(name=perm_name, cu=cu)
    return permission


@perms_router.put(
    '/{perm_name}',
    dependencies=[Depends(deps.HasPermission(['permission:update']))]
)
def update_permission(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    perm_name: str,
    perm_data: schemas.PermissionUpdate,
) -> schemas.PermissionSchema:

    return cruds.update_permission(cu=cu, name=perm_name, update_data=perm_data)


@perms_router.delete(
    '/{perm_name}',
    dependencies=[Depends(deps.HasPermission(['permission:delete']))]
)
def delete_permission(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    perm_name: str, 
) -> dict[str, Any]:

    return cruds.delete_permission(cu=cu, name=perm_name)


# ================ Roles ================
@roles_router.post(
    '',
    status_code=201,
    dependencies=[Depends(deps.HasPermission(['role:create']))]
)
def create_role(
    role_data: schemas.RoleCreate,
    cu: CrudUtil = Depends(CrudUtil),
) -> schemas.RoleSchema:
    
    return cruds.create_role(cu=cu, role_data=role_data)


@roles_router.get(
    '',
    dependencies=[Depends(deps.HasPermission(['role:list']))]
)
def list_roles(
    cu: CrudUtil = Depends(CrudUtil),
    skip: int = 0,
    limit: int = 100,
) -> schemas.RoleList:

    return cruds.list_role(cu=cu, skip=skip, limit=limit)


@roles_router.get(
    '/{role_name}',
    dependencies=[Depends(deps.HasPermission(['role:read']))]
)
def role_detail(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    role_name: str,
) -> schemas.RoleSchema:

    return cruds.get_role_by_name(cu=cu, name=role_name)


@roles_router.put(
    '/{role_name}',
    dependencies=[Depends(deps.HasPermission(['role:update']))]
)
def update_role(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    role_name: str,
    role_data: schemas.RoleUpdate,
) -> schemas.RoleSchema:

    return cruds.update_role(cu=cu, name=role_name, update_data=role_data)


@roles_router.delete(
    '/{role_name}',
    dependencies=[Depends(deps.HasPermission(['role:delete']))]
)
def delete_role(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    role_name: str, 
) -> dict[str, Any]:
    
    return cruds.delete_role(cu=cu, name=role_name)


@roles_router.delete(
    '/{role_name}/permissions',
    dependencies=[Depends(deps.HasPermission(['role:update']))]
)
def remove_permission_from_role(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    role_name: str,
    perms_to_delete: schemas.RemoveRolePermission,
) -> schemas.RoleSchema:
    role = cruds.get_role_by_name(cu=cu, name=role_name)
    perms = perms_to_delete.dict()['permissions']
    for perm_name in perms:
        perm = cruds.get_perm_by_name(cu=cu, name=perm_name)
        if perm:
            try:
                role.permissions.remove(perm)
            except ValueError:
                pass

    cu.db.commit()
    cu.db.refresh(role)
    return role


# ================ Groups ================
@groups_router.post(
    '',
    status_code=201,
    dependencies=[Depends(deps.HasPermission(['group:create']))]
)
def create_group(
    *,
    cu: CrudUtil = Depends(deps.get_db),
    group_data: schemas.GroupCreate,
) -> schemas.GroupSchema:
    
    return cruds.create_group(cu=cu, group_data=group_data)


@groups_router.get(
    '',
    dependencies=[Depends(deps.HasPermission(['group:read']))]
)
def list_groups(
    cu: CrudUtil = Depends(CrudUtil),
    skip: int = 0,
    limit: int = 100,
) -> schemas.GroupList:
    return cruds.list_group(cu=cu, skip=skip, limit=limit)


@groups_router.get(
    '/{group_name}',
    dependencies=[Depends(deps.HasPermission(['group:read']))]
)
def group_detail(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    group_name: str,
) -> schemas.GroupSchema:
    
    return cruds.get_group_by_name(cu=cu, name=group_name)


@groups_router.put(
    '/{group_name}',
    dependencies=[Depends(deps.HasPermission(['group:update']))]
)
def update_group(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    group_name: str,
    group_data: schemas.GroupUpdate,
) -> schemas.GroupSchema:

    return cruds.update_group(
        cu=cu, 
        name=group_name, 
        update_data=group_data
    )


@groups_router.delete(
    '/{group_name}',
    dependencies=[Depends(deps.HasPermission(['group:delete']))]
)
def delete_group(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    group_name: str,
) -> dict[str, Any]:
    
    return cruds.delete_group(cu=cu, name=group_name)


@groups_router.delete(
    '/{group_name}/roles',
    dependencies=[Depends(deps.HasPermission(['group:update']))]
)
def remove_role_from_group(
    *,
    cu: CrudUtil = Depends(CrudUtil),
    group_name: str,
    roles_to_delete: schemas.RemoveGroupRole,
) -> schemas.GroupSchema:
    group = cruds.get_group_by_name(cu=cu, name=group_name)
    roles = roles_to_delete.dict()['roles']
    for role_name in roles:
        role = cruds.get_role_by_name(cu=cu, name=role_name)
        if role:
            try:
                group.roles.remove(role)
            except ValueError:
                pass

    cu.db.commit()
    cu.db.refresh(group)
    return group
