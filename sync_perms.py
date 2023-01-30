#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-24 18:52:40
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from sqlalchemy.orm import Session

from app.access_control import models
from app.config.database import SessionLocal
from app.utils.misc import find_perms



def create_perms(db: Session, perms: list[str]) -> None:
    to_create = []
    for perm in perms:
        db_perm = db.query(models.Permission)\
            .filter(models.Permission.name == perm).first()
        
        if not db_perm:
            to_create.append(models.Permission(name=perm))
    
    input(f"press enter to create permissions: {[perm.name for perm in to_create]}")
    db.add_all(to_create)
    db.commit()


def main() -> None:
    db: Session = SessionLocal()
    create_perms(db, find_perms())
    db.close()


if __name__ == '__main__':
    main()

