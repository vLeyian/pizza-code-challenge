from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder.indent = 2  # For better readability in JSON responses

migrate = Migrate(app, db)

db.init_app(app)

# Define RESTful resources
api = Api(app)

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.serialize() for restaurant in restaurants])

    def post(self):
        data = request.json
        new_restaurant = Restaurant(name=data['name'], address=data['address'])
        db.session.add(new_restaurant)
        db.session.commit()
        return jsonify(new_restaurant.serialize()), 201

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        return jsonify(restaurant.serialize()), 200

    def delete(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.serialize() for pizza in pizzas])

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.json
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        price = data.get('price')

        if not all([pizza_id, restaurant_id, price]):
            return {'errors': ['Missing pizza_id, restaurant_id, or price']}, 400

        try:
            price = int(price)
        except ValueError:
            return {'errors': ['Price must be an integer']}, 400

        if not 1 <= price <= 30:
            return {'errors': ['Price must be between 1 and 30']}, 400

        restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id, restaurant_id=restaurant_id, price=price)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.serialize()), 201

api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)
