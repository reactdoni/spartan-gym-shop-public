from flask import render_template, Blueprint, redirect, url_for
from models import Product
from app import spartan_image_logo

product_bp = Blueprint("product_bp", __name__)

@product_bp.route('/product/<int:product_id>')
def product(product_id):
    product_query = Product.query.filter_by(id=product_id).first()

    if not product_query:
        return redirect(url_for('home_bp.home'))
    
    return render_template('product.html', product_name=product_query.name, product_id=product_query.id, product_img=product_query.img_url, product_price=product_query.price, product_flavours=product_query.flavours, product_description=product_query.description, product_stock=product_query.stock, spartan_image_logo=spartan_image_logo)