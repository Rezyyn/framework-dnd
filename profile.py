from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from forms import ProfileForm
from models import db, User
import os

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        if form.profile_picture.data:
            profile_picture_path = os.path.join('static/profile_pics', form.profile_picture.data.filename)
            form.profile_picture.data.save(profile_picture_path)
            current_user.profile_picture = profile_picture_path
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('profile.html', title='Profile', form=form)
