from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.dependencies.dependencies as deps
from app.access_control import cruds, models, schemas



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
    dependencies=[Depends(deps.HasPermission(['can_create_permission']))]
)
async def create_permission(
    perm_data: schemas.PermissionCreate,
    dba: Session = Depends(deps.get_db)
) -> schemas.PermissionSchema:

    return cruds.create_permission(db=dba, perm_data=perm_data)


@perms_router.get(
    '',
    dependencies=[Depends(deps.HasPermission(['can_view_permission']))]
)
def list_permissions(
    dba: Session = Depends(deps.get_db)
) -> list[schemas.PermissionSchema]:

    return dba.query(models.Permission).all()


@perms_router.get(
    '/{perm_name}',
    dependencies=[Depends(deps.HasPermission(['can_view_permission']))]
)
def permission_detail(
    perm_name: str, 
    dba: Session = Depends(deps.get_db)
) -> schemas.PermissionSchema:

    permission = cruds.get_perm_by_name(name=perm_name, db=dba)
    if not permission:
        raise HTTPException(
            status_code=404,
            detail='Permission not found'
        )
    return permission


@perms_router.put(
    '/{perm_name}',
    response_model=schemas.PermissionSchema,
    dependencies=[Depends(deps.HasPermission(['can_modify_permission']))]
)
def update_permission(
    perm_name: str,
    perm_data: schemas.PermissionUpdate,
    dba: Session = Depends(deps.get_db)
):
    permission = cruds.get_perm_by_name(name=perm_name, db=dba)
    if not permission:
        raise HTTPException(
            status_code=404,
            detail='Permission not found'
        )
    perm_update_dict = perm_data.dict(exclude_unset=True)
    if len(perm_update_dict) < 1:
        raise HTTPException(
            status_code=400,
            detail='Invalid request'
        )
    for key, value in perm_update_dict.items():
        setattr(permission, key, value)
    dba.commit()
    dba.refresh(permission)
    return permission


@perms_router.delete(
    '/{perm_name}',
    dependencies=[Depends(deps.HasPermission(['can_delete_permission']))]
)
def delete_permission(perm_name: str, dba: Session = Depends(deps.get_db)):
    permission = cruds.get_perm_by_name(db=dba, name=perm_name)
    if not permission:
        raise HTTPException(
            status_code=404,
            detail='Permission not found'
        )
    dba.query(models.Permission). \
        filter(models.Permission.name == perm_name). \
        delete()
    dba.commit()
    return {'detail': 'Permission deleted successfully.'}


# ================ Roles ================
@roles_router.post(
    '',
    status_code=201,
    response_model=schemas.RoleSchema,
    dependencies=[Depends(deps.HasPermission(['can_create_role']))]
)
def create_role(
    role_data: schemas.RoleCreate,
    dba: Session = Depends(deps.get_db)
):
    try:
        role = cruds.create_role(db=dba, role_data=role_data)
    except IntegrityError as e:
        raise HTTPException(
            status_code=403,
            detail='Duplicate role not allowed'
        )
    else:
        return role


@roles_router.get(
    '',
    response_model=List[schemas.RoleSchema],
    dependencies=[Depends(deps.HasPermission(['can_view_role']))]
)
def list_roles(dba: Session = Depends(deps.get_db)):
    return dba.query(models.Role).all()


@roles_router.get(
    '/{role_name}',
    response_model=schemas.RoleSchema,
    dependencies=[Depends(deps.HasPermission(['can_view_role']))]
)
def role_detail(role_name: str, dba: Session = Depends(deps.get_db)):
    role = cruds.get_role_by_name(name=role_name, db=dba)
    if not role:
        raise HTTPException(
            status_code=404,
            detail='Role not found'
        )
    return role


@roles_router.put(
    '/{role_name}',
    response_model=schemas.RoleSchema,
    dependencies=[Depends(deps.HasPermission(['can_modify_role']))]
)
def update_role(
    role_name: str,
    role_data: schemas.RoleUpdate,
    dba: Session = Depends(deps.get_db)
):
    role = cruds.get_role_by_name(name=role_name, db=dba)
    if not role:
        raise HTTPException(
            status_code=404,
            detail='Role not found'
        )
    role_dict = role_data.dict(exclude_unset=True)
    try:
        perms = role_dict.pop('permissions')
    except KeyError:
        pass
    else:
        for perm_name in perms:
            perm = cruds.get_perm_by_name(name=perm_name, db=dba)
            if perm:
                role.permissions.append(perm)

    for key, value in role_dict.items():
        setattr(role, key, value)
    dba.commit()
    dba.refresh(role)
    return role


@roles_router.delete(
    '/{role_name}',
    dependencies=[Depends(deps.HasPermission(['can_delete_role']))]
)
def delete_role(role_name: str, dba: Session = Depends(deps.get_db)):
    role = cruds.get_role_by_name(db=dba, name=role_name)
    if not role:
        raise HTTPException(
            status_code=404,
            detail='Role not found'
        )
    dba.query(models.Role). \
        filter(models.Role.name == role_name). \
        delete()
    dba.commit()
    return {'detail': 'Role deleted successfully.'}


@roles_router.delete(
    '/{role_name}/permissions',
    response_model=schemas.RoleSchema,
    dependencies=[Depends(deps.HasPermission(['can_delete_role']))]
)
def remove_permission_from_role(
    role_name: str,
    perms_to_delete: schemas.RemoveRolePermission,
    dba: Session = Depends(deps.get_db)
):
    role = cruds.get_role_by_name(db=dba, name=role_name)
    if not role:
        raise HTTPException(
            status_code=404,
            detail='Role not found'
        )
    perms = perms_to_delete.dict(exclude_unset=True)['permissions']
    for perm_name in perms:
        perm = cruds.get_perm_by_name(name=perm_name, db=dba)
        if perm:
            try:
                role.permissions.remove(perm)
            except ValueError:
                pass

    dba.commit()
    dba.refresh(role)
    return role


# ================ Groups ================
@groups_router.post(
    '',
    status_code=201,
    response_model=schemas.GroupSchema,
    dependencies=[Depends(deps.HasPermission(['can_create_group']))]
)
def create_group(
    group_data: schemas.GroupCreate,
    dba: Session = Depends(deps.get_db)
):
    try:
        group = cruds.create_group(db=dba, group_data=group_data)
    except IntegrityError as e:
        raise HTTPException(
            status_code=403,
            detail='Duplicate group not allowed'
        )
    else:
        return group


@groups_router.get(
    '',
    response_model=List[schemas.GroupSchema],
    dependencies=[Depends(deps.HasPermission(['can_view_group']))]
)
def list_groups(dba: Session = Depends(deps.get_db)):
    return dba.query(models.Group).all()


@groups_router.get(
    '/{group_name}',
    response_model=schemas.GroupSchema,
    dependencies=[Depends(deps.HasPermission(['can_view_group']))]
)
def group_detail(group_name: str, dba: Session = Depends(deps.get_db)):
    group = cruds.get_group_by_name(name=group_name, db=dba)
    if not group:
        raise HTTPException(
            status_code=404,
            detail='Group not found'
        )
    return group


@groups_router.put(
    '/{group_name}',
    response_model=schemas.GroupSchema,
    dependencies=[Depends(deps.HasPermission(['can_modify_group']))]
)
def update_group(
    group_name: str,
    group_data: schemas.GroupUpdate,
    dba: Session = Depends(deps.get_db)
):
    group = cruds.get_group_by_name(name=group_name, db=dba)
    if not group:
        raise HTTPException(
            status_code=404,
            detail='Group not found'
        )
    group_dict = group_data.dict(exclude_unset=True)
    try:
        roles = group_dict.pop('roles')
    except KeyError:
        pass
    else:
        for role_name in roles:
            role = cruds.get_role_by_name(name=role_name, db=dba)
            if role:
                group.roles.append(role)

    for key, value in group_dict.items():
        setattr(group, key, value)
    dba.commit()
    dba.refresh(group)
    return group


@groups_router.delete(
    '/{group_name}',
    dependencies=[Depends(deps.HasPermission(['can_delete_group']))]
)
def delete_group(group_name: str, dba: Session = Depends(deps.get_db)):
    group = cruds.get_group_by_name(db=dba, name=group_name)
    if not group:
        raise HTTPException(
            status_code=404,
            detail='Group not found'
        )
    dba.query(models.Group). \
        filter(models.Group.name == group_name). \
        delete()
    dba.commit()
    return {'detail': 'Group deleted successfully.'}


@groups_router.delete(
    '/{group_name}/roles',
    response_model=schemas.GroupSchema,
    dependencies=[Depends(deps.HasPermission(['can_delete_group']))]
)
def remove_role_from_group(
    group_name: str,
    roles_to_delete: schemas.RemoveGroupRole,
    dba: Session = Depends(deps.get_db)
):
    group = cruds.get_group_by_name(db=dba, name=group_name)
    if not group:
        raise HTTPException(
            status_code=404,
            detail='Role not found'
        )
    roles = roles_to_delete.dict(exclude_unset=True)['roles']
    for role_name in roles:
        role = cruds.get_role_by_name(name=role_name, db=dba)
        if role:
            try:
                group.roles.remove(role)
            except ValueError:
                pass

    dba.commit()
    dba.refresh(group)
    return group
