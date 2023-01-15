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
from typing import Any
from pydantic.main import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta as SqlModel
from fastapi import HTTPException


class CrudUtil:

    def create_model(
        self,
        db: Session, 
        model_to_create: SqlModel,
        create: BaseModel,
        autocommit: bool = True
    ) -> SqlModel:

        try:

            db_model = model_to_create(**create.dict())
            if not autocommit:
                self.__add_no_commit(db, db_model)
                return db_model
            else:
                self.__add_and_commit(db, db_model)
                return db_model
        
        except IntegrityError as e:
        
            print(e)
            raise HTTPException(
                status_code=403, 
                detail=f"Cannot create {model_to_create.__qualname__}, \
                    possible duplicate or invalid attributes"
            )


    def get_model_or_404(
        self,
        db: Session,
        model_to_get: SqlModel,
        model_conditions: dict[str, Any] = {},
        order_by_column: str = "id",
        order: str = "asc"
    )-> Any:

        try:
            conditions = []
            for field_name in model_conditions:
                if model_conditions[field_name] is not None:
                    conditions.append(and_(getattr(model_to_get, field_name) == \
                        model_conditions[field_name]))
            
            if order != "asc":
                return db.query(model_to_get).filter(and_(*conditions)).\
                    order_by(getattr(model_to_get, order_by_column).desc()).first()
            
            return db.query(model_to_get).filter(and_(*conditions)).first()
        
        except AttributeError:
            raise HTTPException(
                status_code=403, 
                detail=f"Invalid attribute for {model_to_get.__qualname__}"
            )

        except Exception as e:
            print(e)
            raise HTTPException(404, detail=f"{model_to_get.__qualname__} not found")


    def update_model(
        self,
        db: Session, 
        model_to_update: SqlModel, 
        update: BaseModel,  
        update_conditions: dict[str, Any] = {},
        autocommit: bool = True
    )-> Any:

        db_model = self.get_model_or_404(
            db,
            model_to_get=model_to_update,
            model_conditions=update_conditions
        )

        try:

            if not autocommit:
                self.__update_no_commit(db, db_model, update)
                return db_model
            else:
                self.__update_and_commit(db, db_model, update)
                return db_model
        
        except Exception as e:

            print(e)
            raise HTTPException(
                status_code=403, 
                detail=f"{model_to_update.__qualname__} update failed"
            )


    def list_model(
        self,
        db: Session,
        model_to_list: SqlModel,
        list_conditions: dict[str, Any] = {},
        date_range: DateRange | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by_column: str = "id",
        order: str = "asc",
        count_by_column: str = "id",
        join_conditions: dict[str, Any] = {},
        sum_by_column: str | None = None
    ) -> dict[str, Any]:

        try:
            conditions = []
            for field_name in list_conditions:
                if list_conditions[field_name] is not None:
                    conditions.append(and_(getattr(model_to_list, field_name) == \
                        list_conditions[field_name]))
            
            join_models = [ join_model for join_model in join_conditions ]
            for join_model in join_models:
                for field_name in join_conditions[join_model]:
                    if join_conditions[join_model][field_name] is not None:
                        conditions.append(and_(getattr(join_model, field_name) == \
                            join_conditions[join_model][field_name]))

            if date_range:
                conditions\
                    .append(and_(getattr(model_to_list, date_range.column_name) >= \
                    date_range.from_date))
                conditions\
                    .append(and_(getattr(model_to_list, date_range.column_name) <= \
                    date_range.to_date))
            
            if sum_by_column:
                sum_total = self.get_model_sum(
                    db, 
                    model_to_list, 
                    sum_by_column, 
                    model_conditions=list_conditions, 
                    date_range=date_range,
                    join_conditions=join_conditions
                )
            else:
                sum_total = None
            
            try:
                db_model_count = int(
                    self.get_model_count(
                        db, 
                        model_to_list, 
                        count_by_column, 
                        list_conditions,
                        date_range, 
                        join_conditions=join_conditions
                    )
                )

                querier = db.query(model_to_list)
                for join_model in join_models:
                    querier = querier.join(join_model)

                if order != "asc":
                    
                    model_list = querier.filter(and_(*conditions))\
                        .order_by(getattr(model_to_list, order_by_column)\
                        .desc()).offset(skip).limit(limit).all()
                    
                    return {
                        "model_list": model_list, 
                        "count": db_model_count, 
                        "sum": sum_total
                    }
            
                model_list = querier.filter(and_(*conditions))\
                    .order_by(getattr(model_to_list, order_by_column))\
                    .offset(skip).limit(limit).all()
                
            except Exception as e:
                print(e)
                db_model_count = 0
                model_list = []
            
            return {
                "model_list": model_list, 
                "count": db_model_count, 
                "sum": sum_total
            }
        
        except AttributeError:
            raise HTTPException(
                status_code=403, 
                detail=f"Invalid attribute for {model_to_list.__qualname__}"
            )
        
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=404, 
                detail=f"{model_to_list.__qualname__} not found"
            )


    def delete_model(
        self,
        db: Session, 
        model_to_delete: SqlModel, 
        delete_conditions: dict[str, Any] = {},
        autocommit: bool = True,
    ) -> dict[str, ActionStatus]:

        db_model = self.get_model_or_404(
            db,
            model_to_get=model_to_delete, 
            model_conditions=delete_conditions,
        )
        try:

            if autocommit:
                self.__delete_and_commit(db, db_model)
                return {"status": ActionStatus.success}
            else:
                self.__delete_no_commit(db, db_model)
                return {"status": ActionStatus.success}
            
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=403, 
                detail=f"Cannot delete this {model_to_delete.__qualname__}, \
                    check if it's still in use"
            )


    def ensure_unique_model(
        self,
        db: Session, 
        model_to_check: SqlModel, 
        unique_condition: dict[str, Any],
    ) -> None:
        
        try:

            # try getting the model if it exists
            db_model = self.get_model_or_404(
                db, 
                model_to_get=model_to_check, 
                model_conditions=unique_condition
            )

            # if it does raise an exception
            if db_model:
                raise HTTPException(
                    status_code=409, 
                    detail=f"{model_to_check.__qualname__} already exists"
                )

        except HTTPException as e:
            # 404 is expected if the model does not exist, 
            # otherwise raise any other exception
            if e.status_code != 404:
                raise e


    def get_model_sum(
        self,
        db: Session,
        model: SqlModel,
        column_to_sum: str,
        model_conditions: dict[str, Any] = {},
        date_range: DateRange | None = None,
        join_conditions: dict[str, Any] = {}
    ) -> float:
        try:
            conditions = []
            if model_conditions:
                for field_name in model_conditions:
                    if model_conditions[field_name] is not None:
                        conditions.append(and_(getattr(model, field_name) == \
                            model_conditions[field_name]))
            
            join_models = [ join_model for join_model in join_conditions ]
            for join_model in join_models:
                for field_name in join_conditions[join_model]:
                    if join_conditions[join_model][field_name]  is not None:
                        conditions.append(and_(getattr(join_model, field_name) == \
                            join_conditions[join_model][field_name]))
            
            if date_range:
                conditions.append(and_(getattr(model, date_range.column_name)\
                    >= date_range.from_date))
                conditions.append(and_(getattr(model, date_range.column_name)\
                    <= date_range.to_date))
            
            querier = db.query(func.sum(getattr(model, column_to_sum)))
            for join_model in join_models:
                querier = querier.join(join_model)

            if conditions:
                db_sum = querier.filter(and_(*conditions)).one()
        
            else:
                db_sum = querier.one()
        
            db_sum = db_sum[0]
            if not db_sum:
                return float(0)
            return float(db_sum)
        
        except AttributeError:
        
            raise HTTPException(
                status_code=403, 
                detail="Invalid server request"
            )
        
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=404, 
                detail=f"Could not retrieve sum of {column_to_sum}. Record not found"
            )


    def get_model_count(
        self,
        db: Session,
        model_to_count: SqlModel,
        column_to_count_by: str,
        model_conditions: dict[str, Any] = {},
        date_range: DateRange | None = None,
        join_conditions: dict[str, Any] = {}
    ) -> int:

        try:
            conditions = []
            if model_conditions:
                for field_name in model_conditions:
                    if model_conditions[field_name] is not None:
                        conditions.append(and_(getattr(model_to_count, field_name) == \
                            model_conditions[field_name]))
            
            join_models = [ join_model for join_model in join_conditions ]
            for join_model in join_models:
                for field_name in join_conditions[join_model]:
                    if join_conditions[join_model][field_name] is not None:
                        conditions.append(and_(getattr(join_model, field_name) == \
                            join_conditions[join_model][field_name]))
            
            if date_range:
                conditions\
                    .append(and_(getattr(model_to_count, date_range.column_name) >= \
                    date_range.from_date))
                
                conditions\
                    .append(and_(getattr(model_to_count, date_range.column_name) <= \
                    date_range.to_date))
            
            querier = db.query(func.count(getattr(model_to_count, column_to_count_by)))

            for join_model in join_models:
                querier = querier.join(join_model)

            if conditions:

                db_count = querier.filter(and_(*conditions)).one()
        
            else:

                db_count = querier.one()
        
            db_count = db_count[0]

            if not db_count:
                return 0
            
            return int(db_count)
        
        except AttributeError:

            raise HTTPException(
                status_code=403, 
                detail=f"Invalid attribute provided for {model_to_count.__qualname__}"
            )
            
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=404, 
                detail=f"Could not retrieve count of {column_to_count_by}. \
                    Record not found"
            )


    def __add_and_commit(
        self,
        db: Session, 
        model_to_add: SqlModel
    ) -> None:

        db.add(model_to_add)
        db.commit()
        db.refresh(model_to_add)


    def __add_no_commit(
        self,
        db: Session, 
        model_to_add: SqlModel
    ) -> None:

        db.add(model_to_add)
        db.flush()


    def __update_and_commit(
        self,
        db: Session, 
        model_to_update: SqlModel, 
        update: BaseModel
    ) -> None:

        update_dict = update.dict(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(model_to_update, key, value)
        
        db.commit()
        db.refresh(model_to_update)


    def __update_no_commit(
        self,
        db: Session, 
        model_to_update: SqlModel, 
        update: BaseModel
    ) -> None:

        update_dict = update.dict(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(model_to_update, key, value)
        
        db.flush()


    def __delete_and_commit(
        self,
        db: Session, 
        model_to_delete: SqlModel
    ) -> None:

        db.delete(model_to_delete)
        db.commit()


    def __delete_no_commit(
        self,
        db: Session, 
        model_to_delete: SqlModel
    ) -> None:

        db.delete(model_to_delete)
        db.flush()


# todo: merge with count
# def get_model_like_column_count(
#     db: Session,
#     model: SqlModel,
#     column: str,
#     model_conditions: dict[str, Any] = {},
#     date_range: DateRange | None = None
# ) -> Any:
#     try:
#         conditions = []
#         if model_conditions:
#             for field_name in model_conditions:
#                 if model_conditions[field_name] is not None:
#                     conditions.append(and_(getattr(model, field_name)\
#                         .ilike(f"%{model_conditions[field_name]}%")))
        
#         if date_range:

#             conditions.append(and_(getattr(model, date_range.column_name) >= \
#                 date_range.from_date))

#             conditions.append(and_(getattr(model, date_range.column_name) <= \
#                 date_range.to_date))
        
#         if conditions:
#             db_count = db.query(func.count(getattr(model, column)))\
#                 .filter(and_(*conditions)).one()
    
#         else:
#             db_count = db.query(func.count(getattr(model, column))).one()
    
#         db_count = db_count[0]
        
#         if not db_count:
#             return float(0)
        
#         return db_count

#     except AttributeError:
#         raise HTTPException(
#             status_code=403, 
#             detail="Invalid server request"
#         )
        
#     except Exception as e:
#         print(e)
#         raise HTTPException(
#             status_code=404, 
#             detail=f"Could not retrieve count of {column}. Record not found"
#         )


# # todo: merge with list model
# def list_models_and_filter_by_likeness(
#     db: Session,
#     model: Any,
#     fields: dict[str, Any],
#     model_name: str,
#     date_range: DateRange | None = None,
#     skip: int = 0,
#     limit: int = 100,
#     order_by: str = "id",
#     order: str = "asc"
# ) -> Any:
#     try:
#         conditions = []
#         for field_name in fields:
#             if fields[field_name] is not None:
#                 conditions.append(and_(getattr(model, field_name)\
#                     .ilike(f"%{fields[field_name]}%")))
        
#         if date_range:
#             conditions.append(and_(getattr(model, date_range.column_name) >= \
#                 date_range.from_date))
            
#             conditions.append(and_(getattr(model, date_range.column_name) <= \
#                 date_range.to_date))
        
#         if order != "asc":
#             return db.query(model).filter(and_(*conditions))\
#                 .order_by(getattr(model, order_by)\
#                 .desc()).offset(skip).limit(limit).all()
        
#         return db.query(model).filter(and_(*conditions))\
#             .offset(skip).limit(limit).all()

#     except AttributeError:
#         raise HTTPException(
#             status_code=403, 
#             detail="Invalid server request"
#         )
    
#     except Exception as e:
#         print(e)
#         raise HTTPException(
#             status_code=404, 
#             detail=f"{model_name} not found"
#         )
