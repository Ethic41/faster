from typing import Any
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from app.config.database import Base
from app.mixins.columns import BaseMixin


user_group = Table('user_group', Base.metadata,
    Column('group_id', String(length=50), ForeignKey('groups.uuid')),
    Column('user_id', String(length=50), ForeignKey('users.uuid'))
)


class User(BaseMixin, Base):
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    old_password_hash = Column(String(255))
    firstname = Column(String(255))
    lastname = Column(String(255))
    middlename = Column(String(255))
    phone = Column(String(50))
    is_active =  Column(Boolean, default=True)
    can_login = Column(Boolean, default=False, server_default="0", nullable=False)

    groups: Any = relationship("Group", secondary=user_group)
    

class PasswordReset(BaseMixin, Base):
    email = Column(String(255), unique=True, nullable=False)
    expires = Column(DateTime, nullable=False)
