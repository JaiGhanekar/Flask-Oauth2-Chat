import unittest
from flask_testing import TestCase
from app import create_app, init_client, init_whitelist
from app import oauth
from app import socketio
from app.models import *
from app.utils import *
from app.main import *
class APITest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def setUp(self):
      db.create_all()
      self.client = self.app.test_client()

    def create_app(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = self.TESTING
        app.secret_key = 'secret'
        app.config['WTF_CSRF_ENABLED']= False
        db.init_app(app)
        with app.app_context():
            db.create_all() 
            init_client() 
            init_whitelist()
            app.add_url_rule('/api/users', 'signup', signup, methods=['POST'])
            app.add_url_rule('/api/users','get_users', get_users, methods=['GET'])
            app.add_url_rule('/api/me', 'me', me, methods=['GET'])
            app.add_url_rule('/test','test', test, methods=['GET'])
            app.add_url_rule('/api/rooms', 'new_room', new_room, methods=['POST'])
            app.add_url_rule('/api/rooms','get_rooms', get_rooms_api, methods=['GET'])
            app.add_url_rule('/oauth/token','access_token', access_token, methods=['GET', 'POST'])
            return app

    def token(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = User(name = name, email = email, password = password)

      if user not in db.session:
        db.session.add(user)
        db.session.commit()

      client_id = 'eG4umCQ3qUTYmQX8SfnkPEbwwGjTOx6TyXifc1FJ'
      client_secret = 'A3hzmToONsEfWp0jWxtk6HWJmvrrC5hT40WPbRwAbNJfZ5E5f0'
      grant_type = 'password'
      response = self.client.post('/oauth/token', data = dict(username = email, password = password, client_id = client_id, client_secret = client_secret, grant_type = grant_type))

      data = response.get_json()
      return data['access_token']
    

    def test_get_users(self):
        response = self.client.get("/api/users?access_token=" + self.token())
        self.assert200(response)

    def test_create_user(self):
        email = 'randomuser@gmail.com'
        name = 'random user'
        password = 'somethingrandom'
        response = self.client.post('/api/users', data = dict(email = email, name = name, password = password))
        data = response.get_json()
        assert response.status_code == 201

    def test_get_me(self):
        response = self.client.get('/api/me?access_token=' + self.token())
        self.assert200(response)
      
    def test_get_test(self):
        response = self.client.get('/test')
        self.assert200(response)

    def test_new_room(self):
        email = 'jaighanekar1@gmail.com'
        name = 'Jai Ghanekar'
        password = 'somethingrandom'
        user1 = create_user(name = name, email = email, password = password)

        email = 'jaighanekar122@gmail.com'
        name = 'Jai Ghanekar'
        password = 'somethingrandom'
        user2 = create_user(name = name, email = email, password = password)

        response = self.client.post('/api/rooms', data = dict(users = ','.join([str(user1.id), str(user2.id)]), name = 'somethingrandom', access_token = self.token()))
        assert response.status_code == 201
    
    def test_get_rooms(self):
        response = self.client.get('/api/rooms?access_token=' + self.token())
        self.assert200(response)

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()