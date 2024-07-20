from flask import render_template, Blueprint, redirect, flash, url_for, request
from flask_login import login_required, current_user
from models import User, db
from app import bcrypt, is_current_user_admin

from app import is_current_user_admin

admin_users_bp = Blueprint("admin_users_bp", __name__)

@admin_users_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    error = ""

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    admin = request.form['admin']

    if User.query.filter_by(username=username).first():
        error = 'Username already taken'
        flash(error, 'danger')
            
    elif User.query.filter_by(email=email).first():
        error = 'Email already taken'
        flash(error, 'danger')

    if error == "":
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        register = User(username=username, email=email, password=hashed_password, admin=True if admin == 'yes' else False)
        db.session.add(register)
        db.session.commit()

        flash('Successfully created new user', 'success')

    return redirect(url_for('admin_users_bp.admin_users'))


@admin_users_bp.route('/update_user/id=<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    admin = request.form['admin']

    user = User.query.filter_by(id=user_id).first()

    changes = False
    if username != user.username:
        user.username = username
        changes = True

    if email != user.email:
        user.email = email
        changes = True

    if password != user.password:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_password
        changes = True

    if admin != user.admin:
        changes = True
        user.admin = True if admin == 'yes' else False

    if changes:
        db.session.commit()

    return redirect(url_for('admin_users_bp.admin_users'))

@admin_users_bp.route('/admin_users')
@login_required
def admin_users():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_users_bp.route('/delete_user/id=<int:user_id>')
@login_required
def delete_user(user_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    if user_id == current_user.id:
        flash("You can't delete your own account", "warning")
        return redirect(url_for('home_bp.home'))
    
    user = User.query.filter_by(id=user_id).first()

    if user:
        if user.admin == True:
            flash("You can't delete an admin account", "warning")
            return redirect(url_for('home_bp.home'))
        
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin_users_bp.admin_users'))

@admin_users_bp.route('/admin_user_search', methods=['POST'])
@login_required
def admin_user_search():
    if not is_current_user_admin():  
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    search_query = request.form.get('q')

    # Filter users by search query
    users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()

    # Render the template with users
    return render_template('admin_users.html', users=users)