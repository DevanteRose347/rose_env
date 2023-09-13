from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# internal imports
from rose_shop.models import (
    Customer,
    Car,
    CarOrder,
    Order,
    db,
    car_schema,
    cars_schema,
)


# instantiate our blueprint
api = Blueprint(
    "api", __name__, url_prefix="/api"
)  # all of our endpoints need to be prefixed with /api


@api.route("/token", methods=["GET", "POST"])
def token():
    data = request.json

    if data:
        client_id = data[
            "client_id"
        ]  # looking for the key of client_id on the dictionary passed to us
        access_token = create_access_token(identity=client_id)
        return {"status": 200, "access_token": access_token}

    else:
        return {"status": 400, "message": "Missing Client Id. Try Again"}


# creating our READ data request for shop
@api.route("/shop")
@jwt_required()
def get_shop():
    shop = (
        Car.query.all()
    )  # list of objects, we can't send a list of objects through api calls

    response = cars_schema.dump(
        shop
    )  # takes our list of objects and turns it into a list of dictionaries
    return jsonify(
        response
    )  # jsonify essentially stringifies the list to send to our frontend


# creating our READ data request for orders READ associated with 'GET'
@api.route("/order/<cust_id>")
@jwt_required()
def get_order(cust_id):
    # We need to grab all the order_ids associated with the customer
    # Grab all the cars on that particular order

    carorder = CarOrder.query.filter(CarOrder.cust_id == cust_id).all()

    data = []

    # need to traverse to grab all the cars from each order
    for order in carorder:
        # order is the carorder object so has a car_id associated with it

        car = Car.query.filter(Car.car_id == order.car_id).first()

        car_data = car_schema.dump(car)  # change this from an object to a dictionary

        car_data["quantity"] = order.quantity  # coming from the carorder table
        car_data[
            "order_id"
        ] = order.order_id  # want to associate this car with a specific order
        car_data[
            "id"
        ] = order.carorder_id  # need to make cars unique even if they are the same car

        data.append(car_data)

    return jsonify(data)


# create our CREATE data request for orders, usually associated with 'POST'
@api.route("/order/create/<cust_id>", methods=["POST"])
@jwt_required()
def create_order(cust_id):
    data = request.json

    customer_order = data["order"]
    print(customer_order)

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)

    # looping through the customer order list of dictionaries for each car
    for car in customer_order:
        carorder = CarOrder(
            car["car_id"],
            car["quantity"],
            car["price"],
            order.order_id,
            customer.cust_id,
        )
        db.session.add(carorder)

        # add price from our carorder table to increment our total order price
        order.increment_order_total(carorder.price)

        # decrement the available amount of that specific car in our shop
        current_car = Car.query.filter(Car.car_id == car["car_id"]).first()
        current_car.decrement_quantity(car["quantity"])

    db.session.commit()

    return {"status": 200, "message": "New Order was created!"}


# create our UPDATE route for our order, usually associated with 'PUT'


@api.route("/order/update/<order_id>", methods=["PUT", "POST"])
@jwt_required()
def update_order(order_id):
    # try:

    data = request.json
    new_quantity = int(data["quantity"])
    car_id = data["car_id"]

    carorder = CarOrder.query.filter(
        CarOrder.order_id == order_id, CarOrder.car_id == car_id
    ).first()
    order = Order.query.get(order_id)  # .get() is specific for ids
    car = Car.query.get(car_id)

    # update the car price based on the new quantity
    carorder.set_price(car.price, new_quantity)

    diff = abs(carorder.quantity - new_quantity)

    # based on if the new quantity is higher or lower we either new to decrement or increment total car quantity & order cost

    if carorder.quantity < new_quantity:
        car.decrement_quantity(diff)  # decrease our available inventory
        order.increment_order_total(
            carorder.price
        )  # our order total is going to be more

    elif carorder.quantity > new_quantity:
        car.increment_quantity(diff)  # increase our available inventory
        car.decrement_order_total(carorder.price)  # our order total is going to be less

    carorder.update_quantity(new_quantity)

    db.session.commit()

    return {"status": 200, "message": "Order was successfully updated!"}

    # except:

    #     return {
    #         'status': 400,
    #         'message': 'Unable to process your request. Please try again!'
    #     }


# create our DELETE route for our order, associated with 'DELETE' method


@api.route("/order/delete/<order_id>", methods=["DELETE"])
@jwt_required()
def delete_item_order(order_id):
    data = request.json
    car_id = data["car_id"]

    carorder = CarOrder.query.filter(
        CarOrder.order_id == order_id, CarOrder.car_id == car_id
    ).first()

    order = Order.query.get(order_id)
    car = Car.query.get(car_id)

    order.decrement_order_total(
        carorder.price
    )  # order total is gonna be less expensive
    car.increment_quantity(carorder.quantity)  # add back to inventory

    db.session.delete(carorder)
    db.session.commit()

    return {"status": 200, "message": "Order was successfully deleted!"}
