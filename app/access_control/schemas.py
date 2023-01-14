from typing import List, Optional
from pydantic import BaseModel

from app.mixins.schemas import BaseUACSchemaMixin
from app.utils.custom_validators import lowercased



class PermissionCreate(BaseModel):
    name: str
    description: Optional[str]

    _val_name = lowercased("name")


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    _val_name = lowercased("name")


class PermissionSchema(BaseUACSchemaMixin):
    
    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str]

    _val_name = lowercased("name")


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]]

    _val_name = lowercased("name")


class RemoveRolePermission(BaseModel):
    permissions: List[str]


class RoleSchema(BaseUACSchemaMixin):
    permissions: List[PermissionSchema]
    
    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    name: str
    description: Optional[str]

    _val_name = lowercased("name")


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[List[str]]

    _val_name = lowercased("name")


class RemoveGroupRole(BaseModel):
    roles: List[str]


class GroupSchema(BaseUACSchemaMixin):
    roles: List[RoleSchema]
    
    class Config:
        orm_mode = True


class GroupOutSchema(BaseUACSchemaMixin):
    
    class Config:
        orm_mode = True

