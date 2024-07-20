from flask import Flask, request, jsonify
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import psycopg2
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'auth_bp.login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS")
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL")
app.config['JSON_AS_ASCII'] = os.getenv("JSON_AS_ASCII")

app.config["SQLALCHEMY_DATABASE_URI"] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

#################### image saving platform ###############
cloudinary_img_url = os.getenv("CLOUDINARY_IMAGES_URL")

cloudinary.config(
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key = os.getenv("CLOUDINARY_API_KEY"),
  api_secret = os.getenv("CLOUDINARY_API_SECRET")
)
###########################################################

#connect to database
conn = psycopg2.connect('')

query_sql = 'SELECT VERSION()'

cur = conn.cursor()
cur.execute(query_sql)

version = cur.fetchone()[0]
print(version)

# initialize database
db = SQLAlchemy(app)

s = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))

# initialize bcrypt for pw hashing
bcrypt = Bcrypt(app)

#initialize mail sender
mail = Mail(app)

# request limiter here

def is_current_user_admin():
    return current_user.admin

spartan_text_logo = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_TEXT_LOGO")).build_url()
spartan_text_image_logo = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_TEXT_IMAGE_LOGO")).build_url()
spartan_header_one = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_HEADER_ONE")).build_url()
spartan_mail_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_MAIL_ICON")).build_url()
spartan_card_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_CARD_ICON")).build_url()
spartan_header_two = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_HEADER_TWO")).build_url()
spartan_kargo_express = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_CARGO_ICON")).build_url()
spartan_image_logo = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_IMAGE_LOGO")).build_url()
spartan_authentic = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_IMAGE_AUTHENTIC")).build_url()
spartan_delivery_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_DELIVERY_ICON")).build_url()
spartan_logo_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_LOGO_ICON")).build_url()
spartan_products_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_PRODUCTS_ICON")).build_url()
spartan_new_icon = cloudinary.CloudinaryImage(os.getenv("CLOUDINARY_LOGOS_PATH") + os.getenv("CLOUDINARY_NEW_ICON")).build_url()

from orders import orders_bp
from home import home_bp
from cart import cart_bp
from auth import auth_bp
from admin_orders import admin_orders_bp
from admin_users import admin_users_bp
from admin_suppliers import admin_suppliers_bp
from admin_sales import admin_sales_bp
from admin_products import admin_products_bp
from admin_categories import admin_categories_bp
from product import product_bp
from category import category_bp

app.register_blueprint(orders_bp)
app.register_blueprint(home_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_users_bp)
app.register_blueprint(admin_suppliers_bp)
app.register_blueprint(admin_sales_bp)
app.register_blueprint(admin_orders_bp)
app.register_blueprint(admin_products_bp)
app.register_blueprint(admin_categories_bp)
app.register_blueprint(product_bp)
app.register_blueprint(category_bp)

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()