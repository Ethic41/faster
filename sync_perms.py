#!/usr/bin/env python
# -=-<[ Bismillahirrahmanirrahim ]>-=-
# -*- coding: utf-8 -*-
# @Date    : 2023-01-24 18:52:40
# @Author  : Dahir Muhammad Dahir (dahirmuhammad3@gmail.com)
# @Link    : link
# @Version : 1.0.0


from sqlalchemy.orm import Session
from pathlib import Path
import re

from app.access_control import models
from app.config.database import SessionLocal



def create_perms(db: Session, perms: list[str]) -> None:
    to_create = []
    for perm in perms:
        db_perm = db.query(models.Permission)\
            .filter(models.Permission.name == perm).first()
        
        if not db_perm:
            to_create.append(models.Permission(name=perm))
    db.add_all(to_create)
    db.commit()


def find_perms() -> list[str]:
    app_dir = Path().cwd()

    perms: list[str] = []
    
    for router_file in app_dir.rglob("router.py"):
        with open(router_file, 'r') as file:
            for line in file:
                perm_line = re.findall(r'HasPermission.+', line)
                if perm_line:
                    perms.extend(re.findall(r'\w+:\w+', perm_line[0]))
    
    return perms


def main() -> None:
    db: Session = SessionLocal()
    create_perms(db, find_perms())
    db.close()


if __name__ == '__main__':
    main()