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
    # created_at = db.Column(db.Datetime, default=datetime.utcnow, nullable=False)


    


