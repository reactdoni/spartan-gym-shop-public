from flask_login import UserMixin
import pytz
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import ARRAY

def get_current_time_utc_plus_1():
    tz = pytz.timezone('Europe/Paris')
    return datetime.now(tz).replace(microsecond=0)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)
    city = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    zip = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.Text, nullable=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.Text, nullable=False)
    new = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.Text, nullable=False, default='No product description available')
    stock = db.Column(db.Integer, nullable=False, default=1)
    flavours = db.Column(ARRAY(db.String), nullable=False, default=[])
    category_id = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, nullable=False)

    def serialize(self):
        """
        Serialize the product object into a dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'img_url': self.img_url,
            'new': self.new,
            'description': self.description,
            'stock': self.stock,
            'flavours': self.flavours,
            'supplier_id': self.supplier_id,
            'category_id': self.category_id
        }

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    order_name = db.Column(db.Text, nullable=False)
    order_quantity = db.Column(db.Integer, nullable=False, default=1)
    order_client = db.Column(db.Text, nullable=False)
    order_price = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=get_current_time_utc_plus_1())
    order_finish_date = db.Column(db.DateTime, nullable=True)
    order_status = db.Column(db.Text, nullable=False, default="Processing")
    order_method = db.Column(db.Text, nullable=False)
    order_userid = db.Column(db.Integer, nullable=False)

class Suppliers(db.Model):
    __tablename__ = 'suppliers'
    supplier_id = db.Column(db.Integer, primary_key=True, nullable=False)
    supplier_name = db.Column(db.Text, nullable=False)
    supplier_phone = db.Column(db.Text, nullable=True)
    supplier_address = db.Column(db.Text, nullable=True)