from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_login import LoginManager, current_user
from db import db
from models import User, Question
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
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
from views import auth_bp
from profile import profile_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_id = str(random.randint(1000, 9999))
    questions = Question.query.all()
    rooms[room_id] = {'players': [], 'questions': questions, 'scores': {}}
    return redirect(url_for('room', room_id=room_id))

@app.route('/room/<room_id>')
def room(room_id):
    if room_id not in rooms:
        return "Room not found!", 404
    return render_template('room.html', room_id=room_id)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    rooms[room]['players'].append(username)
    rooms[room]['scores'][username] = 0
    emit('player_joined', {'username': username}, room=room)
    # Optionally send the current players and scores to the new user
    emit('update_scores', rooms[room]['scores'], room=room)
    # Send the first question to the room
    if rooms[room]['questions']:
        question = rooms[room]['questions'].pop(0)
        emit('new_question', {'question': question.question}, room=room)

@socketio.on('answer')
def handle_answer(data):
    room = data['room']
    username = data['username']
    answer = data['answer']
    # Check answer logic here
    if rooms[room]['questions']:
        correct_answer = rooms[room]['questions'][0].answer
        if answer.lower() == correct_answer.lower():
            rooms[room]['scores'][username] += 1
        rooms[room]['questions'].pop(0)
    emit('update_scores', rooms[room]['scores'], room=room)
    # Send the next question if available
    if rooms[room]['questions']:
        question = rooms[room]['questions'].pop(0)
        emit('new_question', {'question': question.question}, room=room)
    else:
        emit('game_over', room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
