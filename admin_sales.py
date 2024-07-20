from flask import render_template, Blueprint, redirect, flash, url_for
from sqlalchemy import func
from models import Order, db
from flask_login import  login_required

from app import is_current_user_admin

admin_sales_bp = Blueprint("admin_sales_bp", __name__)

@admin_sales_bp.route('/admin_sales')
@login_required
def admin_sales():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))
    
    sales_data = db.session.query(
        func.date_trunc('day', Order.order_date).label('date'),
        func.sum(Order.order_quantity).label('total_sales')
    ).group_by(func.date_trunc('day', Order.order_date)).all()

    # Prepare data for Chart.js
    dates = [row.date.strftime('%Y-%m-%d') for row in sales_data]
    sales = [row.total_sales for row in sales_data]

    return render_template('graph.html', dates=dates, sales=sales)
