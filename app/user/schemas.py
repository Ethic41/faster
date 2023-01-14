from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr, validator
from pydantic.fields import Field
from app.mixins.commons import ListBase

from app.mixins.schemas import BaseSchemaMixin
from app.access_control.schemas import GroupSchema, GroupOutSchema
from app.utils.misc import gen_random_password
from app.utils.user import get_password_hash


class UserIn(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: Optional[str]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field("")
    password_hash: str
    firstname: str
    lastname: str
    middlename: Optional[str]
    can_login: bool

    @validator("password")
    def _gen_password(cls, val: str) -> str:
        return gen_random_password()

    @validator("password_hash")
    def _hash_password(cls, val: str, values: dict[str, Any]) -> str:
        return get_password_hash(values["password"])


class UserGroup(BaseModel):
    groups: List[str]


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    middlename: Optional[str] = None
    is_active: Optional[bool] = Field(None)


class SystemUserFilter(BaseModel):
    email: Optional[EmailStr] = Field(None)
    firstname: Optional[str] = Field(None)
    lastname: Optional[str] = Field(None)
    middlename: Optional[str] = Field(None)
    user_group_name: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    has_wallet: Optional[bool] = Field(None)


class ChagePasswordFromDashboard(BaseModel):
    current_password: str
    new_password: str


class UserSchema(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: Optional[str] = ''
    is_active: bool
    is_system_user: bool
    groups: List[GroupSchema]

    @property
    def permissions(self) -> List[str]:
        perms = []
        for group in self.groups:
            for role in group.roles:
                for perm in role.permissions:
                    perms.append(perm.name)
        return list(set(perms))

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    class Config:
        orm_mode = True


class UserOut(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: Optional[str] = ''
    is_active: bool
    is_system_user: bool
    groups: List[GroupOutSchema]

    class Config:
        orm_mode = True


class UserList(ListBase):
    result: List[UserOut]


class ResetPassword(BaseModel):
    password: str


class PasswordChangeOut(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    permissions: Optional[List[str]] = Field(None)


class Login(BaseModel):
    email: str
    password: str