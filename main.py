import sentry_sdk 
from flask import Flask , jsonify ,flash ,render_template
from sentry_sdk import capture_exception
from dbservice import Product,app,db,request,Sale,User
from flask_cors import CORS
import requests, datetime 
from sqlalchemy import func 
import jwt
from functools import wraps





# db.create_all()


sentry_sdk.init(
    dsn="https://8b61a3cfad8c317f540b5ccda550378c@us.sentry.io/4506695596572672",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            sk = str(app.config['SECRET_KEY'])
            data = jwt.decode(token, sk, algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated






# get  all products and store product
@app.route("/product" , methods=["POST","GET","PUT","PATCH","DELETE"] )
@token_required
def prods(current_user):
    if request.method == "GET":
        
        try:
             prods=Product.query.all()
             res = []
             for i in prods:
               res.append({"id": i.id,"name":i.name,"price":i.price})
             return jsonify(res),200
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({"error"}) , 500
        
    elif request.method == "POST":       
        if request.is_json:
            try:  
                    data = request.json

                    username= current_user
                    user =User.query.filter_by(username=username).first()
                    if user:
                        user_id=user.id

                    new_data = Product(name=data['name'], price= data['price'],userid=user_id)
                    db.session.add(new_data)
                    db.session.commit()
                    r = "successfully stored product id %s" , {str(new_data.id)} 
                    res={"result" : r}
                    return jsonify(res),201
            except Exception as e:
                print(e)
                
                return jsonify("error creating product"),505
        else:
            return jsonify("data is not json"),400
    else:
         return jsonify({"error" : "method not allowed"}),403



@app.route('/get-product<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        prd = Product.query.get(product_id)
        if prd:
            return jsonify({
                "id": prd.id,
                "name": prd.name,
                "price": prd.price
            })
        else:
            return jsonify({"error": "Product not found."}), 404
    except Exception as e:
        print(e)
        # capture_exception(e)
        return jsonify({"error": "Internal Server Error"}), 500
    


@app.route('/sales',methods=['GET','POST'])
def sales():
    if request.method == 'GET':
        try:
            sales=Sale.query.all()
            s_dict=[]
            for sale in sales:
                s_dict.append({"id": sale.id, "pid": sale.pid, "quantity": sale.quantity,"created_at": sale.created_at})
            return jsonify(s_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})
    elif request.method == 'POST':
            if request.is_json:
                try:
                    data = request.json
                    new_sale = Sale(pid=data.get(
                        'pid'), quantity=data.get('quantity'))
                    db.session.add(new_sale)
                    db.session.commit()
                    s = "sales added successfully." + str(new_sale.id)
                    sel = {"result": s}
                    return jsonify(sel), 201
                except Exception as e:
                    print(e)
    # capture_exception(e)
                    return jsonify({"error": "Internal Server Error"}), 500
            else:
                return jsonify({"error": "Data is not JSON."}), 400
    else:
        return jsonify({"error": "Method not allowed."}), 400



@app.route("/dashboard", methods=['POST','GET'])
def dashboard():
    # api_key =  "LVVQU33XBR3NBE1U"
    # url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=KES&apikey="+api_key
    
    # data= requests.get(url).json()
    
# Query  get sales per day for line graph
    sales_per_day = db.session.query(
        func.date(Sale.created_at).label('date'),# extracts date from created at
        func.sum(Sale.quantity *Product.price).label('total_sales')# calculate the total number of sales per day
    ).join(Product).group_by(
        func.date(Sale.created_at)
    ).all()
 
    #  to JSON format
    sales_data = [{'date': str(day), 'total_sales': sales}
                  for day, sales in sales_per_day]
    # Query sales per product for bar graph
    sales_per_product = db.session.query(
        Product.name,
        func.sum(Sale.quantity*Product.price).label('sales_product')
    ).join(Sale).group_by(
        Product.name
    ).all()

     #  JSON format
    salesproduct_data = [{'name': name, 'sales_product': sales_product}
                         for name, sales_product in sales_per_product]

    return jsonify({'sales_data': sales_data, 'salesproduct_data': salesproduct_data})

    
        
# route for register
@app.route("/register", methods=['POST', 'GET'])
def register():
 
     
    data=request.json
    u=data['username']
      

    if not User.query.filter_by(username=u).first():
        new_user=User(username=u,password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        r=f'successfully stored: {str(new_user.id)}'
        res={"result" : r}
        return jsonify(res),201
    else:
        return jsonify({"result" : f'username{u} already exists'}),400
    


  

@app.route("/login", methods=['POST'])
def login():
     try:
      data=request.json
      u =data['username']
      p=data['password']
     except:
         return jsonify({"result" : "invalid request"}),400
      
     user= User.query.filter_by(username=u,password=p).first
     if user:
         secret_key = str(app.config['SECRET_KEY'])
         token = jwt.encode({'username': u, 'exp': datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=30)}, secret_key)
        #  login user
         return jsonify({"result" : "success", "access_token" : token}),200
     else:
        #  incorrect credentials
         return jsonify({"result" : "invalid credentials"}),403


    



        
if  __name__ == "__main__":
   with app.app_context():
       db.create_all()
   app.run(debug=True)    


        