from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

app = Flask(__name__)           #used to create a Flask application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)            #used to create a SQLAlchemy database instance and bind it to the Flask application
api = Api(app)                  #used to create a Flask-RESTful API instance and bind it to the Flask application


class UserModel(db.Model):     #used to define the User model for the database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'User (name={self.name}, email={self.email})'
    
user_args = reqparse.RequestParser()  #used to parse the arguments from the request body
user_args.add_argument('name', type=str, help='Name cannot be blank', required=True)
user_args.add_argument('email', type=str, help='Email cannot be blank', required=True)

userFields = {  #used to set serialization order for the output of the API
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

class Users(Resource):  #used to handle the collection of users
    @marshal_with(userFields)  #used to serialize the output of the API
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)  
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args['name'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        return user, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        return user

    @marshal_with(userFields)
    def patch(self, user_id):
        args = user_args.parse_args()
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        user.name = args['name']
        user.email = args['email']
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message='User not found')
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>/')

@app.route('/')  #used to define the home route of the API
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True)