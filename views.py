from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from db import db
from models import User, Role, Question, GeoJSONLayer, Room
from forms import LoginForm, RegistrationForm
from decorators import role_required
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

# Authentication routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Admin routes
@admin_bp.route('/')
@login_required
@role_required('Admin')
def admin():
    users = User.query.all()
    roles = Role.query.all()
    geojson_layers = GeoJSONLayer.query.all()
    rooms = Room.query.all()
    return render_template('admin.html', title='Admin', users=users, roles=roles, geojson_layers=geojson_layers, rooms=rooms)

@admin_bp.route('/user_management')
@login_required
@role_required('Admin')
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

@admin_bp.route('/list_questions')
@login_required
@role_required('Admin')
def list_questions():
    questions = Question.query.all()
    return render_template('list_questions.html', questions=questions)

@admin_bp.route('/add_question', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add_question():
    if request.method == 'POST':
        question_text = request.form['question']
        answer_text = request.form['answer']
        question = Question(question=question_text, answer=answer_text)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.add_question'))
    return render_template('add_question.html')

@admin_bp.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.list_questions'))

@admin_bp.route('/upload_geojson', methods=['POST'])
@login_required
@role_required('Admin')
def upload_geojson():
    file = request.files['geojson_file']
    if file:
        data = file.read().decode('utf-8')
        layer = GeoJSONLayer(name=file.filename, data=data)
        db.session.add(layer)
        db.session.commit()
        flash('GeoJSON file uploaded successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/toggle_layer/<int:layer_id>/<int:room_id>', methods=['POST'])
@login_required
@role_required('Admin')
def toggle_layer(layer_id, room_id):
    layer = GeoJSONLayer.query.get(layer_id)
    room = Room.query.get(room_id)
    if layer and room:
        if layer in room.active_layers:
            room.active_layers.remove(layer)
            action = 'deactivated'
        else:
            room.active_layers.append(layer)
            action = 'activated'
        db.session.commit()
        flash(f'Layer {action} successfully!', 'success')
        socketio.emit('layer_update', {'room_id': room_id}, broadcast=True)
    return redirect(url_for('admin.admin'))

@admin_bp.route('/delete_layer/<int:layer_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_layer(layer_id):
    layer = GeoJSONLayer.query.get(layer_id)
    if layer:
        db.session.delete(layer)
        db.session.commit()
        flash('Layer deleted successfully!', 'success')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/get_geojson/<int:room_id>')
@login_required
def get_geojson(room_id):
    room = Room.query.get(room_id)
    if room:
        features = [json.loads(layer.data) for layer in room.active_layers]
        return jsonify({"type": "FeatureCollection", "features": [feature for layer in features for feature in layer["features"]]})
    return jsonify({"type": "FeatureCollection", "features": []})
