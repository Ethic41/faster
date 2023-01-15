from sqlalchemy.orm import Session

from app.access_control import models, schemas
from app.utils.crud_util import CrudUtil


cu = CrudUtil()

def create_permission(
    db: Session, 
    perm_data: schemas.PermissionCreate
) -> models.Permission:

    cu.ensure_unique_model(db, models.Permission, {"name": perm_data.name})
    permission: models.Permission = cu.create_model(db, models.Permission, perm_data)
    return permission


def get_perm_by_name(
    db: Session, 
    name: str
) -> models.Permission:

    permission: models.Permission = cu.get_model_or_404(
        db, models.Permission, {"name": name}
    )
    return permission


def list_permission(
    db: Session,
    skip: int,
    limit: int,
) -> list[models.Permission]:
    
    permissions: list[models.Permission] = cu.list_model(
        db=db,
        model_to_list=models.Permission,
        skip=skip,
        limit=limit
    )["model_list"]



def create_role(
    db: Session, role_data: schemas.RoleCreate
) -> models.Role:

    cu.ensure_unique_model(db, models.Role, {"name": role_data.name})
    role: models.Role = cu.create_model(db, models.Role, role_data)
    return role


def get_role_by_name(
    db: Session, name: str
) -> models.Role:

    role: models.Role = cu.get_model_or_404(db, models.Role, {"name": name})
    return role


def create_group(
    db: Session, group_data: schemas.GroupCreate
) -> models.Group:

    cu.ensure_unique_model(
        db, 
        model_to_check=models.Group, 
        unique_condition={"name": group_data.name}
    )

    group: models.Group = cu.create_model(
        db, 
        model_to_create=models.Group, 
        create=group_data
    )
    return group


def get_group_by_name(db: Session, name: str) -> models.Group:
    group: models.Group = cu.get_model_or_404(
        db,
        model_to_get=models.Group,
        model_conditions={"name": name}
    )
    return group
