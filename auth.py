from flask import render_template, Blueprint, session, redirect, flash, url_for, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from models import User, db
import requests
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from app import s
from urllib.parse import unquote
from app import bcrypt, spartan_logo_icon, spartan_image_logo, cloudinary_img_url
import re

auth_bp = Blueprint("auth_bp", __name__)

def is_bcrypt_hash(hash_str):
    # Check if the hash starts with a valid prefix and is 60 characters long
    return hash_str.startswith(('$2b$', '$2a$', '$2y$')) and len(hash_str) == 60

def is_valid_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if the password contains at least one digit
    if not re.search(r'\d', password):
        return False
    
    # Check if the password contains at least one letter
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    # Check if the password contains any blank spaces
    if ' ' in password:
        return False
    
    # If all criteria are met, return True
    return True

def is_valid_email(email):
    # Define the regular expression pattern for a valid email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Match the email against the pattern
    if re.match(pattern, email):
        # If the email matches the pattern, it is valid
        return True
    else:
        # If the email does not match the pattern, it is invalid
        return False

def is_valid_username(username):
    # Define the regular expression pattern for a valid username
    # The pattern requires the username to be at least 4 characters long
    # The username should not start with an underscore, number, or special character
    # The username cannot contain blank spaces
    # The username can contain letters, digits, underscores, and hyphens after the first character
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{3,}$'
    
    # Match the username against the pattern
    if re.match(pattern, username):
        # If the username matches the pattern, it is valid
        return True
    else:
        # If the username does not match the pattern, it is invalid
        return False

def send_email(subject, sender, recipient, body):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html', 'utf-8'))  # Specify UTF-8 encoding for the body

    # SMTP settings
    server = smtplib.SMTP(os.getenv("MAIL_SERVER"), os.getenv("MAIL_PORT"))
    server.starttls()
    server.login(sender, os.getenv("MAIL_PASSWORD"))

    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    error = None

    if request.method == 'POST':
        form_password = request.form['password']
        form_email = request.form['email']
        form_username = request.form['username']

        if form_username and form_password and form_email:
            if User.query.filter_by(username=form_username).first():
                error = 'Username already taken'
            
            elif User.query.filter_by(email=form_email).first():
                error = 'Email already taken'
            
            elif not is_valid_email(form_email):
                error = "Email isn't valid"

            elif not is_valid_username(form_username):
                error = "Username isn't valid"

            else:
                if not is_valid_password(form_password):
                    error = 'Password must:\n*Contain atleast 8 characters\n*One digit\n*One letter'

                else:
                    bcrypt_password = bcrypt.generate_password_hash(form_password).decode('utf-8')

                    token = s.dumps(form_email, salt='salt-key')
                    link = url_for('auth_bp.confirm_email', token=token, _external=True)

                    img_url = cloudinary_img_url + os.getenv("CLOUDINARY_LOGO_ICON")
                    response = requests.get(img_url)

                    if response.status_code == 200:
                        logo_data = response.content
                        logo_base64 = base64.b64encode(logo_data).decode('utf-8')

                        msg_title = 'Spartan Shop, account verification'
                        msg_sender = os.getenv("MAIL_USERNAME")
                            
                        with current_app.app_context():
                            msg_body = render_template('verify_email.html', link=link, logo_base64=logo_base64)
                            send_email(msg_title, msg_sender, form_email, msg_body.encode('utf-8'))

                    register = User(username=form_username, email=form_email, password=bcrypt_password, verified=False)
                    db.session.add(register)
                    db.session.commit()

                    error = 'Successfully registered, activate your account by clicking the link sent to your e-mail'
                    flash(error, 'success')

                    return redirect(url_for('home_bp.home'))

        else:
            error = 'Fill out the form'
        flash(error, 'danger')
    return render_template('register.html', spartan_image_logo=spartan_image_logo)

@auth_bp.route('/request_token', methods=['GET', 'POST'])
def request_token():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    if request.method == 'POST':
        form_email = request.form['email']

        token = s.dumps(form_email, salt='salt-key')
        link = url_for('auth_bp.confirm_email', token=token, _external=True)

        img_url = cloudinary_img_url + os.getenv("CLOUDINARY_LOGO_ICON")
        response = requests.get(img_url)

        if response.status_code == 200:
            logo_data = response.content
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')

            msg_title = 'Spartan Shop, account verification'
            msg_sender = os.getenv("MAIL_USERNAME")
                    
        with current_app.app_context():
            msg_body = render_template('verify_email.html', link=link, logo_base64=logo_base64)
            send_email(msg_title, msg_sender, form_email, msg_body.encode('utf-8'))

        error = 'A new token has been sent to your e-mail. Click it to verify your account'
        flash(error, 'warning')

        return redirect(url_for('home_bp.home'))

    return render_template("token_request.html")

@auth_bp.route('/confirm_email/token=<token>')
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    try:
        email = s.loads(token, salt='salt-key', max_age=86400)
        user = User.query.filter_by(email=email).first()

        if user.verified == True:
            return redirect(url_for('auth_bp.login'))
        
        else:
            user.verified = True
            db.session.commit()
    except:
        return render_template('token_expired.html')
    return render_template('token_verified.html', spartan_logo_icon=spartan_logo_icon)
    
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    error = None

    next_page_encoded = request.args.get('next')

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']

        user = User.query.filter_by(username=username).first()
        if user:
            #checking for future proof error avoiding, when a non bcrypt pw in db is checked it crashes the server
            if is_bcrypt_hash(user.password):
                if bcrypt.check_password_hash(user.password, password):
                    if user.verified:
                        login_user(user)

                        next_page_encoded = request.form.get('next')

                        if next_page_encoded != 'None':
                            next_page = unquote(next_page_encoded)
        
                            return redirect(next_page)
                        else:
                            return redirect(url_for('home_bp.home'))
                    else:
                        error = "Your account isn't verified, a verification link was sent to your e-mail!"
                else:
                    error = 'Incorrect password'
            else:
                error = 'Password not bcrypt hashed, contact an administrator'
        else:
            error = "Username doesn't exist"

        flash(error, 'danger')
    return render_template('login.html', spartan_image_logo=spartan_image_logo)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))
    
    if request.method == 'POST':
        email = request.form['email']

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('E-mail not found, make sure you enter an existing email.', 'danger')
            return render_template('forgot_password.html')

        else:
            token = s.dumps(email, salt='salt-key')
            link = url_for('auth_bp.password_reset', token=token, _external=True)

            img_url = cloudinary_img_url + os.getenv("CLOUDINARY_LOGO_ICON")
            response = requests.get(img_url)

            if response.status_code == 200:
                logo_data = response.content
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')

            msg_title = 'Spartan Shop, requested password change'
            msg_sender = os.getenv("MAIL_USERNAME")
                
            with current_app.app_context():
                msg_body = render_template('reset_password_email.html', link=link, logo_base64=logo_base64)
                send_email(msg_title, msg_sender, user.email, msg_body.encode('utf-8'))  # Encode the email body as UTF-8
            
            flash('An e-mail with instructions to reset your password has been sent, check your inbox', 'success')
            return redirect(url_for('home_bp.home'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/password_reset/token=<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_bp.home'))

    try:
        email_token = s.loads(token, salt='salt-key', max_age=300)
        user = User.query.filter_by(email=email_token).first()

        if request.method == 'POST':
            form_password = request.form['password']

            user.password = bcrypt.generate_password_hash(form_password).decode('utf-8')
            db.session.commit()
            flash('Your password has been successfully reset, login using your new password', 'success')
            return redirect(url_for('auth_bp.login'))

        else:
            return render_template('password_reset.html', token=token)

    except:
        return render_template('token_expired.html')

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home_bp.home'))

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        email = request.form['email']

        if username:
            query = User.query.filter_by(username=username).first()
            if query and query.id != current_user.id:
                flash('Username already taken', 'danger')
                return redirect(url_for('auth_bp.account'))
            
        if email:
            query = User.query.filter_by(email=email).first()
            if query and query.id != current_user.id:
                flash('Email already taken', 'danger')
                return redirect(url_for('auth_bp.account'))
        
        current_user.username = username if username else current_user.username
        current_user.email = email if email else current_user.email
        current_user.password = password if password else current_user.password
        db.session.commit()
        flash('You successfully updated your info', 'success')

        return redirect(url_for('home_bp.home'))
        
    return render_template('account.html')