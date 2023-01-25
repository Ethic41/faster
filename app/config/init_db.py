from getpass import getpass
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError

from app.user import models as users_models
from app.access_control import models as ac_models
from app.utils.user import get_password_hash

def init_db(db: Session) -> None:
    while True:
        email = input('Enter superadmin email: ')
        if len(email) > 0:
            try:
                validate_email(email)
            except EmailNotValidError:
                print('Email is not valid! Please provide a valid email.\n')
            else:
                break
    
    while True:
        password: str = getpass(
            'Enter superadmin password (it won\'t be visible as you type):\n'
        )
        if len(password) < 8:
            print('Invalid input! Password length must be 8 characters or more.\n')
        else:
            break
    
    firstname = input('Enter superadmin firstname [Super]: ')
    lastname = input('Enter superadmin lastname [Admin]: ')
    middlename = input('Enter superadmin middle name: ')
    
    user_dict = {
        'email': email,
        'firstname': firstname if len(firstname) > 0 else 'Super',
        'lastname': firstname if len(lastname) > 0 else 'Admin',
        'middlename': middlename,
        'password_hash': get_password_hash(password)
    }

    perms = [
        'permission:create', 
        'permission:read', 
        'permission:update',
        'permission:list',
        'permission:delete',
    ]

    role_perms = [
        'role:create', 
        'role:read', 
        'role:update', 
        'role:list',
        'role:delete',
    ]

    group_perms = [
        'group:create', 
        'group:read', 
        'group:update', 
        'group:list',
        'group:delete',
    ]

    admin_perms = [
        'admin:create',
        'admin:read',
        'admin:update',
        'admin:list',
        'admin:delete',
    ]

    """
    Possible roles:
    - owner
    - creator
    - editor
    - viewer
    - lister
    - deleter
    """
    perm_owner = ac_models.Role(name='permission:owner')
    role_owner = ac_models.Role(name='role:owner')
    group_owner = ac_models.Role(name='group:owner')
    admin_owner = ac_models.Role(name='admin:owner')

    for perm_name in perms:
        perm = ac_models.Permission(name=perm_name)
        perm_owner.permissions.append(perm)
        db.add(perm)
    
    for perm_name in role_perms:
        perm = ac_models.Permission(name=perm_name)
        role_owner.permissions.append(perm)
        db.add(perm)
    
    for perm_name in group_perms:
        perm = ac_models.Permission(name=perm_name)
        group_owner.permissions.append(perm)
        db.add(perm)
    
    for perm_name in admin_perms:
        perm = ac_models.Permission(name=perm_name)
        admin_owner.permissions.append(perm)
        db.add(perm)

    super_admin_group = ac_models.Group(name='super_admin_group')
    super_admin_group.roles.append(perm_owner)
    super_admin_group.roles.append(role_owner)
    super_admin_group.roles.append(group_owner)
    super_admin_group.roles.append(admin_owner)

    user = users_models.User(**user_dict)
    user.groups.append(super_admin_group)

    db.add_all([
        perm_owner, 
        role_owner, 
        group_owner, 
        super_admin_group, 
        user
    ])

    db.commit()

