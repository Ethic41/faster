#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-09-20 09:39:38
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from sqlalchemy import Column, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Date
from datetime import date

from app.config.database import Base
from app.mixins.columns import BaseMixin


class NextOfKin(BaseMixin, Base):
    firstname = Column(String(length=45), nullable=False)
    lastname = Column(String(length=45), nullable=False)
    middlename = Column(String(length=45), nullable=True, default="")
    phone = Column(String(length=20), nullable=False)
    address = Column(String(length=255), nullable=False, default="")


class Guarantor(BaseMixin, Base):
    firstname = Column(String(length=45), nullable=False)
    lastname = Column(String(length=45), nullable=False)
    middlename = Column(String(length=45), nullable=True, default="")
    phone = Column(String(length=20), nullable=False)
    address = Column(String(length=255), nullable=False, default="")
    image = Column(String(length=255), nullable=False)

    drivers: relationship = relationship("Driver", back_populates="guarantor")


class UserAccount(BaseMixin, Base):
    user_uuid = Column(String(length=50), ForeignKey('users.uuid', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    nin = Column(String(length=16), ForeignKey("nins.nin"), nullable=True, unique=True)
    image = Column(String(length=255), nullable=False)
    phone = Column(String(length=20), nullable=False)
    address = Column(String(length=255), nullable=False, default="")
    gender = Column(Enum("m", "f", "na", name="gender_type_2"), nullable=False)
    birthdate = Column(Date, nullable=False)
    next_of_kin_uuid = Column(String(length=50), ForeignKey("nextofkins.uuid"), nullable=True)
    creator_uuid = Column(String(length=50), ForeignKey("users.uuid"), nullable=False)

    user: relationship = relationship("User", lazy="joined", foreign_keys=[user_uuid])
    driver: relationship = relationship("Driver", lazy="joined", back_populates="user_account", \
        foreign_keys="Driver.user_account_uuid")
    vehicles: relationship = relationship("Vehicle", lazy="joined", \
        back_populates="owner", foreign_keys="Vehicle.owner_uuid")
    creator: relationship = relationship("User", lazy="joined", foreign_keys=[creator_uuid])


class Driver(BaseMixin, Base):
    user_account_uuid = Column(String(length=50), \
        ForeignKey('useraccounts.uuid', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    complexion = Column(String(length=45), nullable=False)
    # driving_license_number = Column(String(length=45), unique=True, nullable=True, default="")
    registration_date = Column(Date, nullable=False, default=date.today)
    expiry_date = Column(Date, nullable=False)
    association_uuid = Column(String(length=50), \
        ForeignKey("associations.uuid", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    association_number = Column(String(length=45), unique=True, nullable=False)
    vehicle_type_uuid = Column(String(length=50), \
        ForeignKey('taxitemtypes.uuid', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    guarantor_uuid = Column(String(length=50), ForeignKey('guarantors.uuid'), nullable=True)
    unique_key = Column(String(length=50), unique=True, nullable=False)
    qr_code_image = Column(String(length=255), nullable=False)
    creator_uuid = Column(String(length=50), ForeignKey("users.uuid"), nullable=False)

    user_account: relationship = relationship("UserAccount", lazy="joined", \
        back_populates="driver", foreign_keys=[user_account_uuid])
    vehicle_type: relationship = relationship("TaxItemType", lazy="joined", back_populates="vehicle_drivers")
    guarantor: relationship = relationship("Guarantor", lazy="joined", back_populates="drivers")
    association: relationship = relationship("Association", lazy="joined", back_populates="drivers")
    creator: relationship = relationship("User", lazy="joined")

