from flask import render_template, Blueprint, redirect, flash, url_for, request, current_app
from models import db, Order, User, get_current_time_utc_plus_1
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from flask_login import login_required
from app import is_current_user_admin

admin_orders_bp = Blueprint("admin_orders_bp", __name__)

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

@admin_orders_bp.route('/admin_update_order_status', methods=['POST', 'GET'])
@login_required
def admin_update_order_status():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))
    
    if request.method == 'POST':
        new_status = request.form['status']
        id = request.form['id']

        current_order = Order.query.filter_by(order_id=id).first()
        user = User.query.filter_by(id=current_order.order_userid).first()

        orders = Order.query.filter_by(order_id=id).all()

        if new_status != 'Delete':
            if current_order.order_status != 'Finished':

                if len(orders) > 1:
                    for order in orders:
                        order.order_status = new_status

                    if new_status == 'Finished':
                        for order in orders:
                            order.order_finish_date = get_current_time_utc_plus_1()

                else:
                    current_order.order_status = new_status

                    if new_status == 'Finished':
                        current_order.order_finish_date = get_current_time_utc_plus_1()

                client = User.query.filter_by(id=current_order.order_userid).first()

                msg_title = 'Spartan Shop, order status has changed'
                msg_sender = os.getenv("MAIL_USERNAME")
                
                with current_app.app_context():
                    msg_body = render_template('status_email.html', orders=orders, status=new_status, username=client.username, order_id=id)
                    send_email(msg_title, msg_sender, user.email, msg_body.encode('utf-8'))  # Encode the email body as UTF-8

        else:
            for order in orders:
                db.session.delete(order)
            db.session.commit()
            
        db.session.commit()

    return redirect(url_for('admin_orders_bp.admin_orders'))

@admin_orders_bp.route('/admin_orders')
@login_required
def admin_orders():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3
    orders = Order.query.order_by(Order.id.desc()).paginate(page=page, per_page=per_page)

    return render_template('admin_orders.html', orders=orders)

@admin_orders_bp.route('/admin_orders_search', methods=['GET', 'POST'])
@login_required
def admin_orders_search():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3

    orders_all = Order.query.order_by(Order.id.desc()).paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':
            search_query = request.form.get('q')

            # Filter orders by search query
            filtered_orders = Order.query.filter(Order.order_name.ilike(f'%{search_query}%')).order_by(Order.id.desc()).paginate(page=page, per_page=per_page)

            return render_template('admin_orders.html', orders=filtered_orders)
        
        elif action == 'reset':
            return redirect(url_for('admin_orders_bp.admin_orders'))

    return render_template('admin_orders.html', orders=orders_all)
        
@admin_orders_bp.route('/admin_orders_search_by_client', methods=['GET', 'POST'])
@login_required
def admin_orders_search_by_client():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3

    all_orders = Order.query.order_by(Order.id.desc()).paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        client_id = request.form.get('client_id')

        # Filter orders by client_id
        client_orders = Order.query.filter_by(order_userid=client_id).order_by(Order.id.desc()).paginate(page=page, per_page=per_page)

        return render_template('admin_orders.html', orders=client_orders)
    
    return render_template('admin_orders.html', orders=all_orders)