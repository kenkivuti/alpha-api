from datetime import datetime
from flask import Flask , render_template , request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "postgresql://postgres:kenkivuti254@localhost:5432/alpha-products"
db = SQLAlchemy(app)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
# relationship
    sales=db.relationship("Sale",back_populates='products')
    username=db.Column(db.String,db.ForeignKey('users.username'),nullable=False)
    user=db.relationship("User", backref="products")
    

class Sale(db.Model):
    __tablename__='sales'
    id=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow ,nullable=False)
    # relationship
    products=db.relationship("Product",back_populates='sales')
    

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(255),unique=True)
    password=db.Column(db.String(255),nullable=False)

    def __repr__(self):
      return f"<User(name='{self.name}', email='{self.email}', password='{self.password}')>"


