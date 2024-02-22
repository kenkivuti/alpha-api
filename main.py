import sentry_sdk 
from flask import Flask , jsonify
from sentry_sdk import capture_exception
from dbservice import Product,app,db,request,Sale
from flask_cors import CORS


# db.create_all()


sentry_sdk.init(
    dsn="https://8b61a3cfad8c317f540b5ccda550378c@us.sentry.io/4506695596572672",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

CORS(app)

# get  all products and store product
@app.route("/product" , methods=["POST","GET","PUT","PATCH","DELETE"] )
def prods():
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
                    new_data = Product(name=data['name'], price= data['price'])
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
        


        
if  __name__ == "__main__":
   with app.app_context():
       db.create_all()
   app.run(debug=True)    


        