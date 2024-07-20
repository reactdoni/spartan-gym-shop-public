from flask import render_template, Blueprint, session, redirect, flash, url_for, request
from flask_login import current_user
from models import Product, Order, db
from flask_login import login_required
from sqlalchemy import desc
import datetime
import random
from app import spartan_image_logo

cart_bp = Blueprint("cart_bp", __name__)

# 12/2022 format
def card_invalid_or_has_expired(expiryDate):
    today = datetime.date.today()
    todayYear = today.year
    todayMonth = today.month

    month, year = expiryDate.split('/')

    if int(month) < 1 or int(month) > 12:
        return True
    
    if int(year) < todayYear or (int(year) == todayYear and int(month) < todayMonth):
        return True

    return False

@cart_bp.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', [])
    total_items = len(cart)

    total_products = Product.query.count()

    # Define the number of random products you want to retrieve
    num_random_products = 3  # Change this value as needed

    # If the number of random products requested is greater than the total number of products,
    # set it to the total number of products
    if num_random_products > total_products:
        num_random_products = total_products

    # Generate a list of random indices to select random products
    random_indices = random.sample(range(1, total_products + 1), num_random_products)

    # Query the database for random products using the random indices
    random_products = Product.query.filter(Product.id.in_(random_indices)).all()
    
    return render_template('cart.html', cart=cart, spartan_image_logo=spartan_image_logo, total_items=total_items, random_products=random_products)

@cart_bp.route('/empty_cart')
@login_required
def empty_cart():
    session.pop('cart', None)
    return redirect(url_for('cart_bp.view_cart'))

@cart_bp.route('/add_to_cart/product_id=<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    
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
        flash('Product added to the cart', 'success')

    return redirect(url_for('home_bp.home'))

@cart_bp.route('/quantity_up/product_id=<int:product_id>')
@login_required
def quantity_up(product_id):
    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == product_id:
            # Check if 'quantity' key exists
            if 'quantity' in item:
                item['quantity'] = item['quantity'] + 1
    session['cart'] = cart
    return redirect(url_for('cart_bp.view_cart'))

@cart_bp.route('/quantity_down/product_id=<int:product_id>')
@login_required
def quantity_down(product_id):
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            # Check if 'quantity' key exists and use max function to prevent negative values
            if 'quantity' in item:
                item['quantity'] = max(1, item['quantity'] - 1)
    session['cart'] = cart

    return redirect(url_for('cart_bp.view_cart'))

@cart_bp.route('/fillout', methods=['GET', 'POST'])
@login_required
def fillout():
    error = ""

    cart = session.get('cart', [])

    if not cart:
        error = "Cart is empty"
        flash(error, 'warning')
        return redirect(url_for('home_bp.home'))

    if request.method == 'POST':

        city = request.form['city']
        address = request.form['address']
        zip_code = request.form['zip_code']
        phone_number = request.form['phone_number']

        method = request.form['paymentMethod']

        if method == 'delivery':
            delivery_name = request.form['deliveryName']

            if not delivery_name.replace(' ', '').isalpha():
                error = "The name musn't include any digits"

        else:
            card_name = request.form['cardName']
            card_number = request.form['cardNumber']
            card_cvv = request.form['cardCVV']
            card_expiry = request.form['cardExpiry']

            if not card_name.replace(' ', '').isalpha():
                error = "The name musn't include any digits"

            if not card_number.replace(' ', '').isdigit():
                error = "The credit card numbers mustn't contain any letters"

            if not len(card_number) == 19:
                error = "The credit card must have 16 digits"
            
            if not card_cvv.isdigit():
                error = "The CVV number mustn't contain any letters"

            if not len(card_cvv) == 3:
                error = "The CVV number must have 3 digits"

            if card_invalid_or_has_expired(card_expiry):
                error = "Your card has expired"

        if error:
            flash(error, 'danger')
            return redirect(url_for('cart_bp.fillout'))
        
        current_user.city = city
        current_user.address = address
        current_user.zip = zip_code
        current_user.phone = phone_number

        userid = current_user.id
        next_order_id = get_next_order_id()

        for item in cart:
            newOrder = Order(order_id=next_order_id,order_name=item["name"], order_quantity=item["quantity"],order_client=current_user.username, order_price=item["price"], order_method=method, order_userid=userid)
            db.session.add(newOrder)
        db.session.commit()
        
        flash('Order successfully completed', 'success')
        session.pop('cart', None)

        return redirect(url_for('home_bp.home'))

    return render_template('fillout.html', cart=cart, user=current_user)

def get_next_order_id():
    max_order_id = db.session.query(db.func.max(Order.order_id)).scalar()
    if max_order_id is None:
        return 1
    else:
        return max_order_id + 1

@cart_bp.route('/orders')
@login_required
def orders():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3
    orders = Order.query.order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

    return render_template('orders.html', orders=orders)

def is_current_user_admin():
    return current_user.admin

@cart_bp.route('/orders_search', methods=['GET', 'POST'])
@login_required
def orders_search():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3

    orders_all = Order.query.order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':
            search_query = request.form.get('q')

            # Filter orders by search query
            filtered_orders = Order.query.filter(Order.order_name.like(f'%{search_query}%')).order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

            return render_template('orders.html', orders=filtered_orders)
        
        elif action == 'reset':
            return redirect(url_for('orders_bp.orders_search'))

    return render_template('orders.html', orders=orders_all)
        
@cart_bp.route('/orders_search_by_client', methods=['GET', 'POST'])
@login_required
def orders_search_by_client():
    if not is_current_user_admin():
        flash('You have to be an admin to access this site', 'warning')
        return redirect(url_for('home_bp.home'))

    page = request.args.get('page', 1, type=int)
    per_page = 3

    all_orders = Order.query.order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        client_id = request.form.get('client_id')

        # Filter orders by client_id
        client_orders = Order.query.filter_by(order_userid=client_id).order_by(desc(Order.id)).paginate(page=page, per_page=per_page)

        return render_template('orders.html', orders=client_orders)
    
    return render_template('orders.html', orders=all_orders)


def get_cart_count():
    cart = session.get('cart', [])

    if cart:
        return len(cart)
    else:
        return 0


@cart_bp.route('/remove_from_cart/product_id=<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', [])

    for item in cart:  # Iterate over cart, not session
        if item['id'] == product_id:  # Use product_id instead of hardcoding 1
            cart.remove(item)
            break

    session['cart'] = cart  # Update the 'cart' key in the session with the modified cart

    return redirect(url_for('cart_bp.view_cart'))
