from flask import render_template, Blueprint, redirect, url_for, request,jsonify
from models import Category, Product
from sqlalchemy import func
from app import spartan_image_logo

category_bp = Blueprint("category_bp", __name__)

@category_bp.route('/category/<int:category_id>')
def category(category_id):
    category_query = Category.query.filter_by(id=category_id).first()

    if not category_query:
        return redirect(url_for('home_bp.home'))
    
    products = Product.query.filter_by(category_id=category_id)
    
    lowest_price = Product.query.with_entities(func.min(Product.price)).filter_by(category_id=category_id).scalar()
    highest_price = Product.query.with_entities(func.max(Product.price)).filter_by(category_id=category_id).scalar()

    return render_template('category.html', category_name=category_query.name, category_id=category_query.id, products=products, spartan_image_logo=spartan_image_logo, lowest_price=lowest_price, highest_price=highest_price)

@category_bp.route('/category_filter/<int:category_id>')
def category_filter(category_id):
    category_query = Category.query.filter_by(id=category_id).first()

    if not category_query:
        return redirect(url_for('home_bp.home'))
    
    # Get filter parameters from query string
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Query products with optional filtering
    query = Product.query.filter_by(category_id=category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()

    lowest_price = Product.query.with_entities(func.min(Product.price)).filter_by(category_id=category_id).scalar()
    highest_price = Product.query.with_entities(func.max(Product.price)).filter_by(category_id=category_id).scalar()
    
    # Return filtered products as JSON response
    return jsonify(products=[product.serialize() for product in products], lowest_price=lowest_price, highest_price=highest_price)
