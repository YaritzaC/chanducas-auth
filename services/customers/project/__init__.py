import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .utils import split_url
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, url_for, jsonify, request, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Blueprint, current_app


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')


app = Flask(__name__)
api = Blueprint('api', __name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()

class ValidationError(ValueError):
    pass

@app.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message' : e.args[0]})
    response.status_code = 400
    return response

@app.errorhandler(404)
def not_found(e):
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': 'invalid resource URI'})
    response.status_code = 404
    return response;

@app.errorhandler(405)
def method_not_supported(e):
    response = jsonify({'status': 405, 'error': 'Method not supported',
                        'message': 'The method is not supported'})
    response.status_code = 405
    return response;

@app.errorhandler(500)
def internal_server_error(e):
    response = jsonify({'status': 500, 'error': 'Internal server error',
                        'message': 'e.args[0]'})
    response.status_code = 500
    return response;

@auth.verify_password
def verify_password(username, password):
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    return g.user.verify_password(password)

@api.before_request
@auth_token.login_required
def before_request():
    pass

@auth.error_handler
def unauthorized():
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': 'please authenticate'})
    response.status_code = 401
    return response

@app.route('/get-auth-token')
@auth.login_required
def get_auth_token():
    return jsonify({'token': g.user.generate_password_token()})

@auth_token.verify_password
def verify_auth_token(token, unused):
    g.user = User.verify_auth_token(token)
    return g.user is not None

@auth_token.error_handler
def unauthorized_token():
    response = jsonify({'status': 401, 'error': 'unauthorized', 'message':
    'please send you  authentication token'})
    response.status_code = 401
    return response

class ValidationError(ValueError):
    pass

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_password_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id':self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data  = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def get_url(self):
        return url_for('get_customer', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name,
            'orders_url': url_for('get_customer_orders', id=self.id,
                                  _external=True)
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid customer: missing ' + e.args[0])
        return self


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    items = db.relationship('Item', backref='product', lazy='dynamic')

    def get_url(self):
        return url_for('get_product', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid product: missing ' + e.args[0])
        return self


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            index=True)
    date = db.Column(db.DateTime, default=datetime.now)
    items = db.relationship('Item', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')

    def get_url(self):
        return url_for('get_order', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'customer_url': self.customer.get_url(),
            'date': self.date.isoformat() + 'Z',
            'items_url': url_for('get_order_items', id=self.id,
                                 _external=True)
        }

    def import_data(self, data):
        try:
            self.date = datetime_parser.parse(data['date']).astimezone(
                tzutc()).replace(tzinfo=None)
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        return self


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           index=True)
    quantity = db.Column(db.Integer)

    def get_url(self):
        return url_for('get_item', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'order_url': self.order.get_url(),
            'product_url': self.product.get_url(),
            'quantity': self.quantity
        }

    def import_data(self, data):
        try:
            endpoint, args = split_url(data['product_url'])
            self.quantity = int(data['quantity'])
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        if endpoint != 'get_product' or not 'id' in args:
            raise ValidationError('Invalid product URL: ' +
                                  data['product_url'])
        self.product = Product.query.get(args['id'])
        if self.product is None:
            raise ValidationError('Invalid product URL: ' +
                                  data['product_url'])
        return self

@api.route('/customers/', methods=['GET'])
def get_customers():
    return jsonify({'customers': [customer.get_url() for customer in
                                  Customer.query.all()]})

@api.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    return jsonify(Customer.query.get_or_404(id).export_data())

@api.route('/customers/', methods=['POST'])
def new_customer():
    customer = Customer()
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({}), 201, {'Location': customer.get_url()}

@api.route('/customers/<int:id>', methods=['PUT'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({})

app.register_blueprint(api)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
