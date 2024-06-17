import re
from random import randint
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_login import LoginManager, current_user, login_required
from db import db
from models import User, Question, Role, GeoJSONLayer, Room
import random
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dnd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Register blueprints
from views import *
from profile import profile_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(profile_bp)

rooms = {}

@app.route('/')
def index():
    active_rooms = rooms
    return render_template('index.html', active_rooms=active_rooms)

@app.route('/create_room', methods=['POST'])
@login_required
def create_room():
    room_id = str(random.randint(1000, 9999))
    questions = Question.query.all()
    rooms[room_id] = {'players': [], 'questions': questions, 'scores': {}, 'messages': []}
    room = Room(name=room_id)
    db.session.add(room)
    db.session.commit()
    return redirect(url_for('room', room_id=room_id))

@app.route('/room/<room_id>')
@login_required
def room(room_id):
    if room_id not in rooms:
        return "Room not found!", 404
    return render_template('room.html', room_id=room_id)

@socketio.on('join')
@login_required
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    rooms[room]['players'].append(username)
    rooms[room]['scores'][username] = 0
    emit('player_joined', {'username': username}, room=room)
    emit('update_scores', rooms[room]['scores'], room=room)
    if rooms[room]['questions']:
        question = rooms[room]['questions'][0]
        emit('new_question', {'question': question.question}, room=room)

@socketio.on('answer')
@login_required
def handle_answer(data):
    room = data['room']
    username = data['username']
    answer = data['answer']
    if rooms[room]['questions']:
        correct_answer = rooms[room]['questions'][0].answer
        if answer.lower() == correct_answer.lower():
            rooms[room]['scores'][username] += 1
        rooms[room]['questions'].pop(0)
    emit('update_scores', rooms[room]['scores'], room=room)
    if rooms[room]['questions']:
        question = rooms[room]['questions'][0]
        emit('new_question', {'question': question.question}, room=room)
    else:
        emit('game_over', room=room)

def parse_dice_roll(command):
    match = re.match(r'/roll (\d+)d(\d+)', command)
    if match:
        num_dice = int(match.group(1))
        dice_sides = int(match.group(2))
        rolls = [randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        return rolls, total
    return None, None

@socketio.on('send_message')
@login_required
def handle_send_message(data):
    room = data['room']
    username = data['username']
    message = data['message']

    if message.startswith('/roll'):
        rolls, total = parse_dice_roll(message)
        if rolls is not None:
            result_message = f"{username} rolled {message}: {rolls} (Total: {total})"
            rooms[room]['messages'].append({'username': username, 'message': result_message})
            emit('receive_message', {'username': username, 'message': result_message}, room=room)
            return

    rooms[room]['messages'].append({'username': username, 'message': message})
    emit('receive_message', {'username': username, 'message': message}, room=room)

@socketio.on('map_ping')
@login_required
def handle_map_ping(data):
    emit('map_ping', data, room=data['room'])

@socketio.on('layer_change')
def handle_layer_change():
    emit('layer_update', broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
