# In models.py

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    pizzas = relationship("RestaurantPizza", back_populates="restaurant")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'pizzas': [pizza.serialize() for pizza in self.pizzas]
        }

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)
    restaurants = relationship("RestaurantPizza", back_populates="pizza")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        return jsonify(restaurant.serialize())

    def delete(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'))
    price = db.Column(db.Integer, nullable=False)

    restaurant = relationship("Restaurant", back_populates="pizzas")
    pizza = relationship("Pizza", back_populates="restaurants")

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30.")
        return price

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'

# In app.py

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

        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return {'errors': ['Restaurant not found']}, 404

        pizza = Pizza.query.get(pizza_id)
        if not pizza:
            return {'errors': ['Pizza not found']}, 404

        restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id, restaurant_id=restaurant_id, price=price)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.serialize()), 201
