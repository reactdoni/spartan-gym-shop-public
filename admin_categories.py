from flask import render_template, Blueprint, redirect, flash, url_for, request
from models import Category, Product, db
from flask_login import login_required
from app import is_current_user_admin
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

admin_categories_bp = Blueprint("admin_categories_bp", __name__)

@admin_categories_bp.route('/admin_category_search', methods=['POST'])
@login_required
def admin_category_search():
    if not is_current_user_admin():  
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))
    
    search_query = request.form.get('q')

    # Filter categories by search query
    categories = Category.query.filter(Category.name.ilike(f'%{search_query}%')).all()

    # store all categories for later to render
    categories_all = []

    # loop through all categories found
    for category in categories:
        # add each category to the main object
        categories_all.append(category)

    products = Product.query.all()

    # Render the template with categories 
    return render_template('admin_categories.html', products=products, categories=categories_all)


@admin_categories_bp.route('/admin_categories')
@login_required
def admin_categories():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    categories = Category.query.all()
    products = Product.query.all()
    return render_template('admin_categories.html', products=products, categories=categories)

@admin_categories_bp.route('/update_category/id=<int:category_id>', methods=['POST'])
@login_required
def update_category(category_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    category_name = request.form['category_name']

    category = Category.query.filter_by(id=category_id).first()

    changes = False
    if category_name:
        category.name = category_name
        changes = True

    if changes:
        db.session.commit()

    return redirect(url_for('admin_categories_bp.admin_categories'))

@admin_categories_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    category_name = request.form['category_name']
    category_image = request.files['category_image']

    result = cloudinary.uploader.upload(category_image, folder=os.getenv("CLOUDINARY_CATEGORY_UPLOAD_PATH"))
    cloudinary_img_url = result['secure_url']

    new_category = Category(name=category_name, img_url=cloudinary_img_url)
    db.session.add(new_category)
    db.session.commit()

    return redirect(url_for('admin_categories_bp.admin_categories'))

@admin_categories_bp.route('/delete_category/id=<int:category_id>')
@login_required
def delete_category(category_id):
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    category = Category.query.filter_by(id=category_id).first()

    if category:
        db.session.delete(category)
        db.session.commit()

    return redirect(url_for('admin_categories_bp.admin_categories'))