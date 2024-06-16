from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from db import db
from models import User, Role, Question, GeoJSONLayer
from forms import LoginForm, RegistrationForm
from decorators import role_required
import json
from werkzeug.security import generate_password_hash, check_password_hash

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
    return render_template('admin.html', title='Admin', users=users, roles=roles, geojson_layers=geojson_layers)

@admin_bp.route('/user_management')
@login_required
@role_required('Admin')
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

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

@admin_bp.route('/toggle_layer/<int:layer_id>', methods=['POST'])
@login_required
@role_required('Admin')
def toggle_layer(layer_id):
    layer = GeoJSONLayer.query.get(layer_id)
    if layer:
        layer.active = not layer.active
        db.session.commit()
        flash(f'Layer {"activated" if layer.active else "deactivated"} successfully!', 'success')
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

@admin_bp.route('/get_geojson')
@login_required
def get_geojson():
    active_layers = GeoJSONLayer.query.filter_by(active=True).all()
    features = [json.loads(layer.data) for layer in active_layers]
    return jsonify(features)
