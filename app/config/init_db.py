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
    
    user_dict = {
        'email': email,
        'firstname': firstname if len(firstname) > 0 else 'Super',
        'lastname': firstname if len(lastname) > 0 else 'Admin',
        'password_hash': get_password_hash(password)
    }

    perms = [
        'can_create_permission', 
        'can_view_permission', 
        'can_modify_permission', 
        'can_delete_permission'
    ]

    role_perms = [
        'can_create_role', 
        'can_view_role', 
        'can_modify_role', 
        'can_delete_role'
    ]

    group_perms = [
        'can_create_group', 
        'can_view_group', 
        'can_modify_group', 
        'can_delete_group'
    ]

    perm_admin = ac_models.Role(name='permission_admin')
    role_admin = ac_models.Role(name='role_admin')
    group_admin = ac_models.Role(name='group_admin')

    for perm_name in perms:
        perm = ac_models.Permission(name=perm_name)
        perm_admin.permissions.append(perm)
        db.add(perm)
    for perm_name in role_perms:
        perm = ac_models.Permission(name=perm_name)
        role_admin.permissions.append(perm)
        db.add(perm)
    for perm_name in group_perms:
        perm = ac_models.Permission(name=perm_name)
        group_admin.permissions.append(perm)
        db.add(perm)

    super_admin_group = ac_models.Group(name='super_admin_group')
    super_admin_group.roles.append(perm_admin)
    super_admin_group.roles.append(role_admin)
    super_admin_group.roles.append(group_admin)
    user = users_models.User(**user_dict)
    user.groups.append(super_admin_group)
    db.add_all([
        perm_admin, 
        role_admin, 
        group_admin, 
        super_admin_group, 
        user
    ])
    db.commit()

