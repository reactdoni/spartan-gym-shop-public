from flask import render_template, Blueprint, redirect, flash, url_for, request, current_app
from flask_login import login_required
from models import Product, Category, Suppliers, db
from distutils.util import strtobool
from cart import remove_from_cart
from app import is_current_user_admin, cloudinary_img_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

admin_products_bp = Blueprint("admin_products_bp", __name__)

# original admin panel index with all products
@admin_products_bp.route('/admin')
@login_required
def admin():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))
    
    products = Product.query.all()
    categories = Category.query.all()
    suppliers = Suppliers.query.all()

    new_products = 0
    for product in products:
        if product.new:
            new_products += 1

    return render_template('admin_index.html', products=products, categories=categories, suppliers=suppliers, total_products=len(products), new_products=new_products, total_categories=len(categories), total_suppliers=len(suppliers))

# admin products search filter
@admin_products_bp.route('/admin_product_search', methods=['POST'])
@login_required
def admin_product_search():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    search_query = request.form.get('q')
    # Filter products by search query
    products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()

    # store all products for later to render
    products_all = []

    # loop through all products found
    for product in products:
        # add each product to the main object
        products_all.append(product)

    categories = Category.query.all()
    suppliers = Suppliers.query.all()

    new_products = 0
    for product in products:
        if product.new:
            new_products += 1

    return render_template('admin_index.html', products=products_all, categories=categories, suppliers=suppliers, total_products=len(products), new_products=new_products, total_categories=len(categories), total_suppliers=len(suppliers))


@admin_products_bp.route('/update_product/id=<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    product = Product.query.get(product_id)
    if not product:
        flash('Product does not exist', 'error')
        return redirect(url_for('admin_products_bp.admin'))

    name = request.form['product_name']
    price = request.form['product_price']
    category_name = request.form['product_category']
    supplier_name = request.form['product_supplier']
    image = request.files['product_image']
    new = request.form['product_new']

    if name:
        product.name = name

    if price:
        product.price = price

    if new:
        product.new = strtobool(new)

    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        if category:
            product.category_id = category.id

    if supplier_name:
        supplier = Suppliers.query.filter_by(supplier_name=supplier_name).first()
        if supplier:
            product.supplier_id = supplier.supplier_id

    if image:
        cloudinary_img_path = cloudinary_img_url + image
        cloudinary.uploader.upload(cloudinary_img_path)

        product.img_url = image # update db

    db.session.commit()

    return redirect(url_for('admin_products_bp.admin'))

@admin_products_bp.route('/delete_product/id=<int:product_id>')
@login_required
def delete_product(product_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this sitee', 'warning')
        return redirect(url_for('home_bp.home'))

    product = Product.query.filter_by(id=product_id).first()

    if product:
        start = 62 # 62 characters of un-needed url https://cloudinary...
        find_extension = product.img_url[62:].index(".") # find the .jpg .png

        cloudinary.uploader.destroy(product.img_url[start:(start+find_extension)], invalidate=True) # remove it from cloudinary
        remove_from_cart(product_id)
        db.session.delete(product)
        db.session.commit()

    return redirect(url_for('admin_products_bp.admin'))

@admin_products_bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    name = request.form['product_name']
    price = request.form['product_price']
    category_name = request.form['product_category']
    supplier_name = request.form['product_supplier']
    new = request.form['product_new']
    image = request.files['product_image']
    stock = request.form['product_stock']
    description = request.form['product_description']
    flavours = request.form['product_flavour']

    if not category_name:
        flash('Category does not exist', 'error')
        return redirect(url_for('admin_products_bp.admin'))
    
    if not supplier_name:
        flash('Supplier does not exist', 'error')
        return redirect(url_for('admin_products_bp.admin'))

    category = Category.query.filter_by(name=category_name).first()
    supplier = Suppliers.query.filter_by(supplier_name=supplier_name).first()

    if not category:
        flash('Category does not exist', 'error')
        return redirect(url_for('admin_products_bp.admin'))
    
    if not supplier:
        flash('Supplier does not exist', 'error')
        return redirect(url_for('admin_products_bp.admin'))

    flavours = [flavour.strip() for flavour in flavours.split(',')] if flavours else []

    # Upload the image to Cloudinary
    result = cloudinary.uploader.upload(image, folder=os.getenv("CLOUDINARY_UPLOAD_PATH"))
    cloudinary_img_url = result['secure_url']

    new_product = Product(name=name, price=price, img_url=cloudinary_img_url, new=strtobool(new), stock=stock, description=description, category_id=category.id, supplier_id=supplier.supplier_id, flavours=flavours)
    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for('admin_products_bp.admin'))