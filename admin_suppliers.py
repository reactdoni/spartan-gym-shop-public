from flask import render_template, Blueprint, redirect, flash, url_for, request
from flask_login import login_required
from models import Product, Suppliers, db
from app import is_current_user_admin

admin_suppliers_bp = Blueprint("admin_suppliers_bp", __name__)

@admin_suppliers_bp.route('/admin_supplier_search', methods=['POST'])
@login_required
def admin_supplier_search():
    if not is_current_user_admin():  
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    search_query = request.form.get('q')

    suppliers = Suppliers.query.filter(Suppliers.supplier_name.ilike(f'%{search_query}%')).all()

    suppliers_all = []

    for supplier in suppliers:
        suppliers_all.append(supplier)

    products = Product.query.all()
 
    return render_template('admin_suppliers.html', products=products, suppliers=suppliers_all)
    
@admin_suppliers_bp.route('/admin_suppliers')
@login_required
def admin_suppliers():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    suppliers = Suppliers.query.all()
    products = Product.query.all()
    return render_template('admin_suppliers.html', products=products, suppliers=suppliers)

@admin_suppliers_bp.route('/update_supplier/id=<int:supplier_id>', methods=['POST'])
@login_required
def update_supplier(supplier_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    if request.method == 'POST':
        supplier_name = request.form['supplier_name']
        supplier_phone = request.form['supplier_phone']
        supplier_address = request.form['supplier_address']

        supplier = Suppliers.query.filter_by(supplier_id=supplier_id).first()

        changes = False
        if supplier_name:
            supplier.supplier_name = supplier_name
            changes = True

        if supplier_address:
            supplier.supplier_address = supplier_address
            changes = True

        if supplier_phone:
            supplier.supplier_phone = supplier_phone
            changes = True    

        if changes:
            db.session.commit()

        return redirect(url_for('admin_suppliers_bp.admin_suppliers'))

@admin_suppliers_bp.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    supplier_name = request.form['supplier_name']
    supplier_phone = request.form['supplier_phone']
    supplier_address = request.form['supplier_address']

    new_supplier = Suppliers(supplier_name=supplier_name, supplier_phone=supplier_phone, supplier_address=supplier_address)
    db.session.add(new_supplier)
    db.session.commit()

    return redirect(url_for('admin_suppliers_bp.admin_suppliers'))

@admin_suppliers_bp.route('/delete_supplier/id=<int:supplier_id>')
@login_required
def delete_supplier(supplier_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    supplier = Suppliers.query.filter_by(supplier_id=supplier_id).first()

    if supplier:
        db.session.delete(supplier)
        db.session.commit()

    return redirect(url_for('admin_suppliers_bp.admin_suppliers'))