from app.core.database import db as database
from app.lms.models import LMSUser, UserRole, Organization
from passlib.hash import bcrypt
import uuid

db = database.get_session()

# Get the first organization
org = db.query(Organization).first()
if not org:
    print('No organization found! Creating one...')
    org = Organization(
        id=uuid.uuid4(),
        name='Ulrich AI',
        subdomain='ulrich',
        is_active=True
    )
    db.add(org)
    db.commit()
    db.refresh(org)

admin = db.query(LMSUser).filter(LMSUser.email == 'admin@ulrich.ai').first()

if admin:
    admin.password_hash = bcrypt.hash('admin123')
    admin.organization_id = org.id
    admin.role = UserRole.SUPER_ADMIN
    db.commit()
    print('Updated existing admin user')
    print('Email: admin@ulrich.ai')
    print('Password: admin123')
    print(f'Organization: {org.name}')
else:
    admin = LMSUser(
        id=uuid.uuid4(),
        organization_id=org.id,
        email='admin@ulrich.ai',
        password_hash=bcrypt.hash('admin123'),
        first_name='Admin',
        last_name='User',
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        email_verified=True
    )
    db.add(admin)
    db.commit()
    print('Created new admin user')
    print('Email: admin@ulrich.ai')
    print('Password: admin123')
    print(f'Organization: {org.name}')

db.close()