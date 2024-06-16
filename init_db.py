from db import db
from models import User, Role, Question, GeoJSONLayer, Room, RoomLayers

def init_db():
    db.create_all()
    # Add any initial data if necessary

if __name__ == '__main__':
    from app import app
    with app.app_context():
        init_db()
