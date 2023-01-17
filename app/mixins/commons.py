#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-24 00:40:54
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from app.utils.custom_validators import currency_out_val
from enum import Enum
from typing import Any, List, Optional


from app.mixins.schemas import BaseSchemaMainMixin, BaseSchemaMixin
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import date


class Gender(str, Enum):
    male = "m"
    female = "f"
    na = "na"


class WalletStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    closed = "closed"


class WalletTxnType(str, Enum):
    credit = "credit"
    debit = "debit"


class PaymentAccountStatus(str, Enum):
    activated = "activated"
    deactivated = "deactivated"
    blacklisted = "blacklisted"


class EnrollmentStatus(str, Enum):
    enrolled = "enrolled"
    not_enrolled = "not_enrolled"


class TaxPayerType(str, Enum):
    registered = "registered"
    unregistered = "unregistered"
class NINImageOut(BaseModel):
    nin: str = Field(..., max_length=16)
    image: str = Field(..., max_length=160)

    class Config:
        orm_mode = True


class UserOut(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: Optional[str] = ''
    is_active: bool
    is_system_user: bool

    class Config:
        orm_mode = True


class VehicleQROut(BaseModel):
    qr_file: str

    class Config:
        orm_mode = True


class DateRange(BaseModel):
    column_name: str
    from_date: date
    to_date: date


class ListBase(BaseModel):
    count: int
    sum: Optional[float] = Field(None)

    _val_sum = currency_out_val("sum")


class TaxItemTypeMin(BaseSchemaMixin):
    name: str = Field(..., max_length=100, min_length=3, description="Tax Item Type Name")
    tax_cycle: int = Field(..., description="Tax Cycle in days, e.g 1 for daily, 7 for weekly e.t.c")
    tax_cycle_name: Optional[str] = Field(None, max_length=100, \
        description="Tax Cycle Name, e.g daily, weekly, monthly")
    license_renewal_cycle: int = Field(..., description="License Renewal Cycle in days e.g 365 for annually")
    taxable_amount: float = Field(..., description="Taxable Amount on item")

    _val_tax_amount = currency_out_val("taxable_amount")


class SubUnitMin(BaseSchemaMixin):
    name: str = Field(..., max_length=45, description="Sub Unit Name")
    display_name: Optional[str] = Field(None, max_length=45, description="Sub Unit Display Name")
    unit_uuid: str = Field(..., description="Unit UUID")

class UnitMin(BaseSchemaMixin):
    unit_name: str = Field(..., max_length=45, description="Unit Name")
    unit_code: str = Field(..., max_length=45, description="Unit Code")
    local_government_uuid: str = Field(..., description="Local Government UUID")
    tax_item_type_uuid: str = Field(..., description="Tax Item Type UUID")


class OrganizationMin(BaseSchemaMixin):
    name: str = Field(..., max_length=100, description="Organization Name")
    display_name: Optional[str] = Field(None, max_length=100, description="Organization Display Name")
    contact_number: str = Field(..., max_length=20, description="Organization Contact Number")


class AssociationMin(BaseSchemaMixin):
    name: str = Field(..., max_length=100, description="Association Name")
    contact_number: str = Field(..., max_length=20, description="Association Contact Number")
    organization_uuid: str = Field(..., description="Organization UUID")
    tax_item_type_uuid: str = Field(..., description="Tax Item Type UUID")


class UserMin(BaseSchemaMixin):
    email: EmailStr
    firstname: str
    lastname: str
    middlename: Optional[str] = ''


class LocalGovernmentMin(BaseSchemaMainMixin):
    name: str = Field(..., max_length=45)
    display_name: str = Field(..., max_length=100)

class DriverMin(BaseSchemaMixin):
    user_account_uuid: str = Field(..., description="unique id of user account")
    complexion: str = Field(..., max_length=20, description="complexion of driver")
    driving_license_number: Optional[str] = Field(None, max_length=45, description="driving license number of driver")
    expiry_date: date = Field(..., description="expiry date of driver")
    association_uuid: str = Field(..., description="unique id of association")
    association_number: str = Field(..., max_length=20, description="association number of driver")
    vehicle_type_uuid: str = Field(..., description="unique id of vehicle type")
    guarantor_uuid: str = Field(..., description="unique id of guarantor")
    unique_key: str = Field(..., description="Unique Key")
    qr_code_image: str = Field(..., max_length=255, description="qr code image of driver")
    creator_uuid: str = Field(..., description="unique id of creator")


class UserAccountMin(BaseSchemaMixin):
    user_uuid: str = Field(..., description="unique id of user")
    next_of_kin_uuid: Optional[str] = Field(None, description="unique id of next of kin")
    nin: Optional[str] = Field(None, max_length=16, description="nin of user")
    image: str = Field(..., max_length=255, description="image of user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    address: str = Field(..., description="address of user")
    gender: Gender
    birthdate: date

    user: UserMin


class UserAccountPhone(BaseModel):
    phone: str = Field(..., max_length=20, description="Phone number of the user")

    class Config:
        orm_mode = True


class GuarantorMin(BaseSchemaMixin):
    firstname: str = Field(..., max_length=45, description="first name of guarantor")
    lastname: str = Field(..., max_length=45, description="last name of guarantor")
    middlename: Optional[str] = Field(None, max_length=45, description="middle name of guarantor")
    phone: str = Field(..., max_length=20, description="phone number of guarantor")
    address: str = Field(..., max_length=100, description="address of guarantor")


class WalletMin(BaseSchemaMixin):
    id: int = Field(None)
    wallet_number: int = Field(..., description="Wallet number")
    owner_uuid: str = Field(..., description="Owner uuid")
    super_wallet_owner_uuid: Optional[str] = Field(None, description="Super wallet owner uuid")
    balance: float = Field(..., description="Wallet balance")
    status: WalletStatus = Field(..., description="Wallet status")

    _balance_val = currency_out_val("balance")


class SuperWalletOwnerMin(BaseSchemaMixin):
    display_name: str = Field(..., description="Display name")
    user_uuid: str = Field(..., description="User uuid")


class WalletTxnMin(BaseSchemaMixin):
    wallet_number: int = Field(..., description="Wallet number")
    type: WalletTxnType = Field(..., description="Transaction type")
    amount: float = Field(..., description="Amount")
    credit_amount: float = Field(..., description="Amount")
    performed_by: str = Field(..., description="Performed by uuid")

    _val_amount = currency_out_val("amount")


class TaxPaymentAccountMin(BaseSchemaMixin):
    tax_payer_uuid: str = Field(..., max_length=45, description="Tax Payer UUID")
    taxed_item_id: str = Field(..., max_length=45, description="Taxed Item ID e.g vehicle id")
    tax_item_type_uuid: str = Field(..., max_length=45, description="Tax Item UUID")
    tax_payer_type: TaxPayerType = Field(..., description="Tax Payer Type")
    paid_till_date: date = Field(..., description="Paid Till Date")
    status: PaymentAccountStatus = Field(None, description="Payment Account Status")


class TaxPaymentTxnMin(BaseSchemaMixin):
    taxed_item_id: str = Field(..., max_length=45, description="Taxed Item ID")
    amount: float = Field(..., gt=0, description="Amount Paid")
    days_paid: int = Field(..., ge=1, description="Number of days the payer is paying for")
    txn_id: str = Field(..., max_length=45, description="Transaction ID")
    txn_receipt: str = Field(..., max_length=100, description="URL to transaction receipt")
    wallet_txn_uuid: str = Field(...)
    tax_item_type_uuid: str = Field(...)
    tax_payer_type: TaxPayerType = Field(..., description="Tax Payer Type")
    txn_date: date = Field(..., description="Transaction Date")
    performed_by: str = Field(..., max_length=45, description="Performed By")

    _val_amount = currency_out_val("amount")


class StakeHolderMin(BaseSchemaMixin):
    name: str = Field(..., max_length=45, description="Stake Holder Name")


class TaxStakeMin(BaseSchemaMixin):
    stake_holder: str = Field(..., max_length=100, description="Tax Stake Holder Name")
    stake_name: str = Field(..., max_length=100, description="Stake Name")
    stake_amount: float = Field(..., description="Stake Amount")
    tax_item_type_name: str = Field(..., max_length=100, description="Tax Item Type Name")

    _val_stake_amount = currency_out_val("stake_amount")


class TaxPaymentBreakdownMin(BaseSchemaMixin):
    stake_holder: str = Field(..., max_length=100)
    stake_name: str = Field(..., max_length=100)
    amount: float = Field(...)
    tax_payment_txn_uuid: str = Field(...)
    txn_date: date = Field(..., description="Transaction Date")
    performed_by: str = Field(..., max_length=45, description="Performed By")

    _val_amount = currency_out_val("amount")


class ThirdPartyTaxInfoMin(BaseSchemaMixin):
    taxed_item_id: str = Field(..., max_length=45, description="Taxed Item ID e.g vehicle id")
    tax_payer_uuid: str = Field(..., max_length=45, description="Owner UUID")
    tax_item_type_uuid: str = Field(..., max_length=45, description="Tax Item Type UUID")
    state_tin: Optional[str] = Field(None, max_length=45, description="State TIN")
    normalized_state_tin: Optional[str] = Field(None, max_length=45, description="Normalized State TIN")
    enrollment_status: EnrollmentStatus = Field(..., description="Tax Enrollment Status")


class UnitFull(UnitMin):
    tax_item_type: TaxItemTypeMin
    sub_units: List[SubUnitMin]
    local_government: LocalGovernmentMin


class SubUnitFull(SubUnitMin):
    unit: UnitMin


class LocalGovernmentFull(LocalGovernmentMin):
    units: List[UnitFull]


class OrganizationFull(OrganizationMin):
    associations: List[AssociationMin]


class AssociationFull(AssociationMin):
    organization: OrganizationMin
    tax_item_type: TaxItemTypeMin


class UserAccountFull(UserAccountMin):
    user: UserMin


class DriverFull(DriverMin):
    user_account: UserAccountMin
    vehicle_type: TaxItemTypeMin
    association: AssociationMin
    guarantor: GuarantorMin


class WalletFull(WalletMin):
    owner: UserMin
    super_wallet_owner: Optional[SuperWalletOwnerMin]


class SuperWalletOwnerFull(SuperWalletOwnerMin):
    user: UserMin
    wallets: List[WalletFull]


class WalletTxnFull(WalletTxnMin):
    wallet: WalletFull
    performer: UserMin


class TaxPaymentAccountFull(TaxPaymentAccountMin):
    tax_payment_txns: List[TaxPaymentTxnMin]
    tax_payer: UserAccountMin


class TaxPaymentTxnVendor(TaxPaymentTxnMin):
    performer: UserMin
    tax_payment_account: TaxPaymentAccountMin
    tax_item_type: TaxItemTypeMin


class TaxPaymentTxnFull(TaxPaymentTxnMin):
    performer: UserMin
    tax_payment_account: TaxPaymentAccountMin
    wallet_txn: WalletTxnMin
    tax_item_type: TaxItemTypeMin
    tax_payment_breakdowns: List[TaxPaymentBreakdownMin]


class StakeHolderFull(StakeHolderMin):
    pass


class TaxStakeFull(TaxStakeMin):
    tax_item_type: TaxItemTypeMin


class TaxPaymentBreakdownFull(TaxPaymentBreakdownMin):
    tax_payment_txn: TaxPaymentTxnMin
    tax_stake: TaxStakeMin


class ThirdPartyTaxInfoFull(ThirdPartyTaxInfoMin):
    tax_item_type: TaxItemTypeMin
    tax_payer: UserAccountMin

