#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2021-05-08 16:51:20
# @Author  : Dahir Muhammad Dahir
# @Description : something cool


from app.mixins.commons import DateRange
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import func
from app.utils.enums import ActionStatus
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic.main import BaseModel

from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from app.interfaces.db import DBModel  # type: ignore


def fully_add(db: Session, model):
    db.add(model)
    db.commit()
    db.refresh(model)


def add_no_commit(db: Session, model):
    db.add(model)
    db.flush()

def update_no_commit(db: Session, model, update_model: BaseModel):
    update_dict: dict = update_model.dict(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(model, key, value)
    
    db.flush()


def fully_delete(db: Session, model):
    db.delete(model)
    db.commit()


def delete_no_commit(db: Session, model):
    db.delete(model)
    db.flush()


def fully_update(db: Session, model, update_model: BaseModel):
    update_dict: dict = update_model.dict(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(model, key, value)
    
    db.commit()
    db.refresh(model)


def create_model(db: Session, model: Any, model_name: str, model_to_create: BaseModel, autocommit=True):
    try:
        db_model = model(**model_to_create.dict())
        if not autocommit:
            add_no_commit(db, db_model)
            return db_model
        else:
            fully_add(db, db_model)
            return db_model
    except IntegrityError as e:
        print(e)
        raise HTTPException(403, detail=f"Cannot create {model_name}, possible duplicate or invalid entry")


def get_model_all(db: Session, model: Any, limit: int, skip: int):
    return db.query(model).offset(skip).limit(limit).all()


def get_model_by_field_all(db: Session, model: Any, model_name: str, field: Dict, limit: int, skip: int):
    try:
        model_field, field_value = field.popitem()
        return db.query(model).filter(getattr(model, model_field) == field_value).offset(skip).limit(limit).all()
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_by_name(db: Session, model: Any, model_name: str, name: str):
    try:
        return db.query(model).filter(model.name == name).one()
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_by_uuid(db: Session, model: Any, model_name: str, uuid: str):
    try:
        return db.query(model).filter(model.uuid == str(uuid)).one()
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_by_id(db: Session, model: Any, model_name: str, id: int):
    try:
        return db.query(model).filter(model.id == id).one()
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_by_nin(db: Session, model: Any, model_name: str, nin: str):
    try:
        return db.query(model).filter(model.nin == nin).first()
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_by_field_first(
    db: Session, 
    model: Any, 
    model_field: str, 
    model_name: str, 
    field_value: Any,
    order_by_field: str = "id",
    order: str = "asc"
):
    try:
        if order != "asc":
            return db.query(model).filter(getattr(model, model_field) == field_value)\
                .order_by(getattr(model, order_by_field).desc()).first()

        return db.query(model).filter(getattr(model, model_field) == field_value).first()
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_column_sum(
    db: Session,
    model: Any,
    column: str,
    model_conditions: Dict = {},
    date_range: Optional[DateRange] = None,
    join_fields: Dict = {}
):
    try:
        conditions = []
        if model_conditions:
            for field_name in model_conditions:
                if model_conditions[field_name] != None:
                    conditions.append(and_(getattr(model, field_name) == model_conditions[field_name]))
        
        join_models = [ join_model for join_model in join_fields ]
        for join_model in join_models:
            for field_name in join_fields[join_model]:
                if join_fields[join_model][field_name]  != None:
                    conditions.append(and_(getattr(join_model, field_name) == join_fields[join_model][field_name]))
        
        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        querier = db.query(func.sum(getattr(model, column)))
        for join_model in join_models:
            querier = querier.join(join_model)

        if conditions:
            db_sum = querier.filter(and_(*conditions)).one()
    
        else:
            db_sum = querier.one()
    
        db_sum = db_sum[0]
        if not db_sum:
            return float(0)
        return db_sum
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
        
    except:
        raise HTTPException(404, detail=f"Could not retrieve sum of {column}. Record not found")


def get_model_column_count(
    db: Session,
    model: Any,
    column: str,
    model_conditions: Dict = {},
    date_range: Optional[DateRange] = None,
    join_fields: Dict = {}
):
    try:
        conditions = []
        if model_conditions:
            for field_name in model_conditions:
                if model_conditions[field_name] != None:
                    conditions.append(and_(getattr(model, field_name) == model_conditions[field_name]))
        
        join_models = [ join_model for join_model in join_fields ]
        for join_model in join_models:
            for field_name in join_fields[join_model]:
                if join_fields[join_model][field_name] != None:
                    conditions.append(and_(getattr(join_model, field_name) == join_fields[join_model][field_name]))
        
        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        querier = db.query(func.count(getattr(model, column)))
        for join_model in join_models:
            querier = querier.join(join_model)

        if conditions:
            db_count = querier.filter(and_(*conditions)).one()
    
        else:
            db_count = querier.one()
    
        db_count = db_count[0]
        if not db_count:
            return float(0)
        return db_count
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
        
    except Exception as e:
        raise HTTPException(404, detail=f"Could not retrieve count of {column}. Record not found")


def get_model_like_column_count(
    db: Session,
    model: Any,
    column: str,
    model_conditions: Dict[str, str] = {},
    date_range: Optional[DateRange] = None
):
    try:
        conditions = []
        if model_conditions:
            for field_name in model_conditions:
                if model_conditions[field_name] != None:
                    conditions.append(and_(getattr(model, field_name).ilike(f"%{model_conditions[field_name]}%")))
        
        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        if conditions:
            db_count = db.query(func.count(getattr(model, column))).filter(and_(*conditions)).one()
    
        else:
            db_count = db.query(func.count(getattr(model, column))).one()
    
        db_count = db_count[0]
        if not db_count:
            return float(0)
        return db_count
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
        
    except:
        raise HTTPException(404, detail=f"Could not retrieve count of {column}. Record not found")


def get_model_by_multi_fields_and(
    db: Session,
    model: Any,
    fields: Dict,
    model_name: str,
    order_by: str = "id",
    order: str = "asc"
):
    try:
        conditions = []
        for field_name in fields:
            if fields[field_name] != None:
                conditions.append(and_(getattr(model, field_name) == fields[field_name]))
        
        if order != "asc":
            return db.query(model).filter(and_(*conditions)).order_by(getattr(model, order_by).desc()).first()
        
        return db.query(model).filter(and_(*conditions)).first()
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def get_model_all_by_multi_fields_and(
    db: Session,
    model: Any,
    fields: Dict[str, str],
    model_name: str,
    date_range: Optional[DateRange] = None,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    order: str = "asc"
):
    try:
        conditions = []
        for field_name in fields:
            if fields[field_name] != None:
                conditions.append(and_(getattr(model, field_name) == fields[field_name]))
        
        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        if order != "asc":
            return db.query(model).filter(and_(*conditions)).order_by(getattr(model, order_by).desc()).offset(skip).limit(limit).all()
        
        return db.query(model).filter(and_(*conditions)).offset(skip).limit(limit).all()
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def list_models_and_filter_by_equality(
    db: Session,
    model: Any,
    fields: Dict,
    model_name: str,
    date_range: Optional[DateRange] = None,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    order: str = "asc",
    count_by_column: str = "id",
    join_fields: Dict = {},
    sum_total_column: Optional[str] = None
):
    try:
        conditions = []
        for field_name in fields:
            if fields[field_name] != None:
                conditions.append(and_(getattr(model, field_name) == fields[field_name]))
        
        join_models = [ join_model for join_model in join_fields ]
        for join_model in join_models:
            for field_name in join_fields[join_model]:
                if join_fields[join_model][field_name] != None:
                    conditions.append(and_(getattr(join_model, field_name) == join_fields[join_model][field_name]))

        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        if sum_total_column:
            sum_total = get_model_column_sum(db, model, sum_total_column, model_conditions=fields, date_range=date_range,\
                join_fields=join_fields)
        else:
            sum_total = None
        
        try:
            db_model_count = int(get_model_column_count(db, model, count_by_column, fields, \
                date_range, join_fields=join_fields))

            querier = db.query(model)
            for join_model in join_models:
                querier = querier.join(join_model)

            if order != "asc":
                result_list = querier.filter(and_(*conditions)).order_by(getattr(model, order_by).desc()).offset(skip).limit(limit).all()
                return {"result": result_list, "count": db_model_count, "sum_total": sum_total}
        
            result_list = querier.filter(and_(*conditions)).order_by(getattr(model, order_by)).offset(skip).limit(limit).all()
        except:
            db_model_count = 0
            result_list = []
        
        return {"result": result_list, "count": db_model_count, "sum_total": sum_total}
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def list_models_and_filter_by_likeness(
    db: Session,
    model: Any,
    fields: Dict[str, str],
    model_name: str,
    date_range: Optional[DateRange] = None,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    order: str = "asc"
):
    try:
        conditions = []
        for field_name in fields:
            if fields[field_name] != None:
                conditions.append(and_(getattr(model, field_name).ilike(f"%{fields[field_name]}%")))
        
        if date_range:
            conditions.append(and_(getattr(model, date_range.column_name) >= date_range.from_date))
            conditions.append(and_(getattr(model, date_range.column_name) <= date_range.to_date))
        
        if order != "asc":
            return db.query(model).filter(and_(*conditions)).order_by(getattr(model, order_by).desc()).offset(skip).limit(limit).all()
        
        return db.query(model).filter(and_(*conditions)).offset(skip).limit(limit).all()
    except AttributeError:
        raise HTTPException(403, detail="Invalid server request")
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def check_model_is_duplicate(db: Session, model: Any, unique_field: Dict, model_name: str):
    key, val = get_key_val_from_dict(unique_field)
    db_model = get_model_by_field_first(db, model, key, model_name, val)
    if db_model:
        raise HTTPException(409, detail=f"{model_name} already exists")
    


def check_model_exists(db: Session, model: Any, field: Dict, model_name: str):
    key, val = get_key_val_from_dict(field)
    db_model = get_model_by_field_first(db, model, key, model_name, val)
    if not db_model:
        raise HTTPException(404, detail=f"{model_name} not found")
    
    return db_model


def get_key_val_from_dict(target_dict: Dict):
    try:
        return target_dict.popitem()
    except:
        raise HTTPException(500, detail="Invalid fields provided")

def get_model_by_email(db: Session, model: Any, model_name: str, email: str):
    try:
        return db.query(model).filter(model.email == email).first()
    except:
        raise HTTPException(404, detail=f"{model_name} not found")


def update_model_by_uuid(db: Session, model: Any, update_model, model_name: str, uuid: str):
    db_model = get_model_by_uuid(db, model, model_name, uuid)
    try:
        fully_update(db, db_model, update_model)
        return db_model
    except:
        raise HTTPException(403, detail=f"{model_name} update failed")


def update_model_by_field(db: Session, model: Any, update_model, model_name: str, field: Dict, autocommit=True):
    field_key, field_value = field.popitem()
    db_model = get_model_by_field_first(db, model, field_key, model_name, field_value)
    try:
        if not autocommit:
            update_no_commit(db, db_model, update_model)
            return db_model
        else:
            fully_update(db, db_model, update_model)
            return db_model
    except:
        raise HTTPException(403, detail=f"{model_name} update failed")


def delete_model_by_uuid(db: Session, model: Any, model_name: str, uuid: str):
    db_model = get_model_by_uuid(db, model, model_name, uuid)
    try:
        fully_delete(db, db_model)
        return {"status": ActionStatus.success}
    except:
        raise HTTPException(403, detail=f"Cannot delete this {model_name}, check if it's still in use")


def delete_model_by_field(db: Session, model: Any, model_name: str, field: Dict, autocommit=True):
    field_key, field_value = field.popitem()
    db_model = get_model_by_field_first(db, model, field_key, model_name, field_value)
    try:
        if autocommit:
            fully_delete(db, db_model)
            return {"status": ActionStatus.success}
        else:
            delete_no_commit(db, db_model)
            return {"status": ActionStatus.success}
    except:
        raise HTTPException(403, detail=f"Cannot delete this {model_name}, check if it's still in use")

