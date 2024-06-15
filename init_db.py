# init_db.py
from app import app
from models import db, User, Map, Layer, Tooltip, ClassSheet, Attribute

with app.app_context():
    db.create_all()
    # Create an admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
