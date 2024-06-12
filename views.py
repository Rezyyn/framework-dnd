from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from db import db
from models import User, Role, Question
from forms import LoginForm, RegistrationForm
from decorators import role_required

auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/admin')
@login_required
@role_required('Admin')
def admin():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin.html', title='Admin', users=users, roles=roles)

@auth_bp.route('/user_management')
@login_required
@role_required('Admin')
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

@auth_bp.route('/add_question', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add_question():
    if request.method == 'POST':
        question_text = request.form['question']
        answer_text = request.form['answer']
        new_question = Question(question=question_text, answer=answer_text)
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('auth.list_questions'))
    return render_template('add_question.html')

@auth_bp.route('/list_questions')
@login_required
@role_required('Admin')
def list_questions():
    questions = Question.query.all()
    return render_template('list_questions.html', questions=questions)

@auth_bp.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('auth.list_questions'))

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('auth.user_management'))
    return render_template('edit_user.html', user=user)

@auth_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('auth.user_management'))
