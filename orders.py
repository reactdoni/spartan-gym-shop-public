from flask import render_template, Blueprint, redirect, flash, url_for, request
from flask_login import current_user
from models import Order
from flask_login import login_required
from sqlalchemy import desc

orders_bp = Blueprint("orders_bp", __name__)

@orders_bp.route('/my_orders')
@login_required
def my_orders():
    if not current_user.is_authenticated:
        flash('You have to be logged in', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3
    orders = Order.query.filter_by(order_userid=current_user.id).order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

    return render_template('my_orders.html', orders=orders)

@orders_bp.route('/my_orders_search', methods=['GET', 'POST'])
@login_required
def my_orders_search():
    if not current_user.is_authenticated:
        flash('You have to be logged in', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3

    orders_all = Order.query.filter_by(order_userid=current_user.id).order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':
            search_query = request.form.get('q')
            print(search_query)

            filtered_orders = Order.query.filter_by(order_userid=current_user.id).filter(Order.order_name.ilike(f'%{search_query}%')).order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

            return render_template('my_orders.html', orders=filtered_orders)
        
        elif action == 'reset':
            return redirect(url_for('orders_bp.my_orders'))

    return render_template('my_orders.html', orders=orders_all)
