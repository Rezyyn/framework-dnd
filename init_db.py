from app import app, db
from models import Role

with app.app_context():
    # Create all the database tables
    db.create_all()

    # Check if the roles already exist to avoid duplicate entries
    if not Role.query.filter_by(name='Admin').first():
        admin_role = Role(name='Admin', permissions='all')
        db.session.add(admin_role)
    
    if not Role.query.filter_by(name='User').first():
        user_role = Role(name='User', permissions='view')
        db.session.add(user_role)

    db.session.commit()
