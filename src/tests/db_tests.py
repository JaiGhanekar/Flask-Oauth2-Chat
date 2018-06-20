import unittest
from flask_testing import TestCase
from app import create_app, init_client, init_whitelist
from app import oauth
from app import socketio
from app.models import *
from app.utils import *
from app.main import *

class DatabaseTest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def setUp(self):
      db.create_all()

    def create_app(self):
       app = Flask(__name__)
       app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
       app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
       app.config['TESTING'] = self.TESTING
       db.init_app(app)

       with app.app_context():
        db.create_all() 
        init_client() 
        init_whitelist()
       return app

    def test_save_user(self):
        email = 'jaighanekar1224@gmail.com'
        name = 'Jai Ghanekar'
        password = 'somethingrandom'
        user = create_user(name,email,password)
        user = User.query.get(user.id)
        assert user in db.session

    def test_create_room(self):
      room = create_room('room')
      assert room in db.session

    def test_get_room(self):
      room = create_room('room')
      rooms = get_rooms()
      assert len(rooms) == 1

    def test_add_user_to_room(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      ru = add_user_to_room(user.id, room.id)
      assert ru in db.session

    def test_user_in_room(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      another =  create_room('another room')
      ru = add_user_to_room(user.id, room.id)
      possible = user_in_room(user.id, room.id)
      assert possible.user_id == user.id and possible.room_id == room.id

      possible = user_in_room(user.id, another.id)
      assert possible is None

    def test_remove_user_from_room(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      ru = add_user_to_room(user.id, room.id)
      assert ru in db.session

      remove_user_from_room(user.id, room.id)
      assert ru not in db.session

    def test_get_users_by_room(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      ru = add_user_to_room(user.id, room.id)
      users = get_users_by_room(room.id)
      assert len(users) == 1 and users[0].id == user.id

    def test_get_rooms_by_user(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      ru = add_user_to_room(user.id, room.id)
      rooms = get_rooms_by_user(user.id)
      assert len(rooms) == 1 and rooms[0].id == room.id

    def test_create_message(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      message = create_message(user.id, room.id, 'from jai')
      assert message in db.session

    def test_get_messages(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      message1 = create_message(user.id, room.id, 'from jai')
      message2 = create_message(user.id, room.id, 'another from jai')
      page = 1
      perpage = 1
      pagination = get_messages(room.id, page, perpage)
      assert len(pagination.items) == 1 and pagination.pages == 2 and pagination.items[0].id == message1.id

    def test_parse_links(self):
      text = 'http://youtube.com'
      links = parse_links(text)
      assert len(links) == 1

    def test_create_sources(self):
        link = 'http://youtube.com'
        sources = create_sources([link])
        assert len(sources) == 1 and sources[0] in db.session and type(sources[0]) is VideoSource

        link = 'https://cdn.history.com/sites/2/2013/12/new-york-city-H.jpeg'
        sources = create_sources([link])
        assert len(sources) == 1 and sources[0] in db.session and type(sources[0]) is ImageSource

    def test_create_metas(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user = create_user(name,email,password)
      room = create_room('room')
      message = create_message(user.id, room.id, 'from jai')
      link = 'http://youtube.com'
      sources = create_sources([link])
      metas = create_metas(message.id, sources)
      assert len(metas) == 1 and metas[0] in db.session and metas[0].message_id == message.id and metas[0].video_id == sources[0].id

      link = 'https://cdn.history.com/sites/2/2013/12/new-york-city-H.jpeg'
      sources = create_sources([link])
      metas = create_metas(message.id, sources)
      assert len(metas) == 1 and metas[0] in db.session and metas[0].message_id == message.id and metas[0].image_id == sources[0].id

    def test_room_with_id(self):
      room = create_room('room')
      rooms = [{'id' : room.id}]
      found = room_with_id(room.id, rooms)
      assert found['id'] == room.id

      nothing = room_with_id(room.id + 1, rooms)
      assert nothing is None

    def test_select_chat_room(self):
      room1 = create_room('room1')
      room2 = create_room('room2')
      rooms = [{'id' : room1.id},{'id': room2.id}]
      found = select_chat_room(rooms, room2.id)
      assert found['id'] == room2.id

      first = select_chat_room(rooms, None)
      assert first['id'] == room1.id

    def test_unique_rooms(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user1 = create_user(name,email,password)

      email = 'jaighanekar12@gmail.com'
      name = 'Other Jai'
      password = 'somethingalsorandom'
      user2 = create_user(name,email,password)

      email = 'jaighanekar@gmail.com'
      name = 'Other Other Jai'
      password = 'somethingalsoalsorandom'
      user3 = create_user(name,email,password)

      room1 = create_room('room1')
      room2 = create_room('room2')
      room3 = create_room('room3')
      room4 = create_room('room4')

      add_user_to_room(user1.id, room1.id)
      add_user_to_room(user3.id, room1.id)
      add_user_to_room(user1.id, room2.id)
      add_user_to_room(user2.id, room2.id)
      add_user_to_room(user2.id, room3.id)
      add_user_to_room(user3.id, room3.id)

      unique = unique_rooms([user1.id, user2.id, user3.id])
      assert len(unique) == 3


    def test_find_room(self):
      email = 'jaighanekar1224@gmail.com'
      name = 'Jai Ghanekar'
      password = 'somethingrandom'
      user1 = create_user(name,email,password)

      email = 'jaighanekar12@gmail.com'
      name = 'Other Jai'
      password = 'somethingalsorandom'
      user2 = create_user(name,email,password)

      email = 'jaighanekar@gmail.com'
      name = 'Other Other Jai'
      password = 'somethingalsoalsorandom'
      user3 = create_user(name,email,password)

      room1 = create_room('room1')
      room2 = create_room('room2')
      room3 = create_room('room3')
      room4 = create_room('room4')

      add_user_to_room(user1.id, room1.id)
      add_user_to_room(user3.id, room1.id)
      add_user_to_room(user1.id, room2.id)
      add_user_to_room(user2.id, room2.id)
      add_user_to_room(user2.id, room3.id)
      add_user_to_room(user3.id, room3.id)

      room_id = find_room([user1.id, user2.id])
      assert room_id == room2.id 

      room_id = find_room([user1.id, user2.id, user3.id])
      assert room_id is None

    def tearDown(self):
        db.session.remove()
        db.drop_all()






if __name__ == '__main__':
    unittest.main()