import sentry_sdk 
from flask import Flask , jsonify
from sentry_sdk import capture_exception
from dbservice import Product,app,db,request


# db.create_all()


sentry_sdk.init(
    dsn="https://8b61a3cfad8c317f540b5ccda550378c@us.sentry.io/4506695596572672",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

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
        
if  __name__ == "__main__":
   with app.app_context():
       db.create_all()
   app.run(debug=True)    


        