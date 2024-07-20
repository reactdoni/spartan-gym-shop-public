from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from models import Product, Category
from sqlalchemy import desc
from flask_login import current_user
from cart import get_cart_count
from app import spartan_text_logo, spartan_new_icon, spartan_header_one, spartan_mail_icon,spartan_card_icon, spartan_header_two, spartan_kargo_express, spartan_image_logo, spartan_authentic, spartan_delivery_icon, spartan_logo_icon, spartan_products_icon

home_bp = Blueprint("home_bp", __name__)

@home_bp.route('/')
def home():

    page = request.args.get('page', 1, type=int)
    per_page = 5
    products = Product.query.order_by(desc(Product.id)).paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    cart = session.get('cart', [])

    return render_template('index.html', products=products, categories=categories, cart=cart, cart_items=get_cart_count(),
                           spartan_text_logo=spartan_text_logo, spartan_mail_icon=spartan_mail_icon,
                           spartan_card_icon=spartan_card_icon, spartan_kargo_express=spartan_kargo_express,
                           spartan_authentic=spartan_authentic, spartan_delivery_icon=spartan_delivery_icon, spartan_products_icon=spartan_products_icon,
                           spartan_header_one=spartan_header_one, spartan_header_two=spartan_header_two, spartan_image_logo=spartan_image_logo, spartan_new_icon=spartan_new_icon)

@home_bp.route('/get_products_from_category')
def get_products_from_category():
    request_category = request.args.get('category')

    query_category = Category.query.filter_by(name=request_category).first()

    if not query_category:
        return "error"

    products = Product.query.filter_by(category_id=query_category.id).all()

    product_list = []
    for product in products:
        product_info = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image": product.img_url
        }
        product_list.append(product_info)
    return jsonify(product_list)

# Define a route to handle adding items to the cart
@home_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if current_user.is_authenticated:
        product_id = request.json.get('product_id')

        # Verify that product_id is not None or empty
        if product_id is None or product_id == '':
            return jsonify({'error': 'Product ID is missing or invalid'}), 400

        product = Product.query.filter_by(id=product_id).first()

        if product:
            cart = session.get('cart', [])

            # Check if the product is already in the cart
            product_in_cart = next((item for item in cart if item['id'] == product.id), None)

            # If the product is not in the cart, add it
            if product_in_cart:
                for item in cart:
                    if item['id'] == product.id:
                        if 'quantity' in item:
                            quantity = item['quantity'] + 1
                            item['quantity'] = quantity
                        else:
                            item['quantity'] = 1
            else:
                cart.append({'id': product.id, 'name': product.name, 'price': int(product.price), 'image': product.img_url, 'quantity': 1})

            session['cart'] = cart

        response = {'message': 'Item added to cart successfully'}

        return jsonify(response), 200
    else:
        return jsonify({'error': 'User not authenticated'}), 401

@home_bp.route('/what_happened')
def what_happened():
    return render_template('what_happened.html')

@home_bp.route('/how_to_order')
def how_to_order():
    return render_template('how_to_order.html')

@home_bp.route('/faq')
def faq():
    return render_template('faq.html')