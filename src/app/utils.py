from .models import *
import re
from urllib.parse import urlparse
import requests
def create_room(name):
    room = Room(name = name)
    db.session.add(room)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
    finally:
        return room

def get_rooms():
    return Room.query.all()

def get_users_by_room(room_id):
    return RoomUser.query.filter_by(room_id = room_id).order_by(RoomUser.user_id).all()

def get_rooms_by_user(user_id):
    return RoomUser.query.filter_by(user_id = user_id).all()

def user_in_room(user_id, room_id):
    return RoomUser.query.filter(RoomUser.user_id == user_id, RoomUser.room_id == room_id).first()
#check if user in room first 
def create_message(user_id, room_id, raw):
    message = Message(user_id = user_id, room_id = room_id, raw = raw)
    db.session.add(message)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
    finally:
        return message

def get_messages(room_id, page, per_page):
    return Message.query.filter_by(room_id = room_id).order_by(Message.created_date.asc()).paginate(page,per_page,error_out=False)

#save meta data functions
def parse_links(s):
    return re.findall(r'(https?://\S+)', s)
    
def _get_netloc(link):
    return urlparse(link).netloc

def _clean_netloc(netloc):
    host = netloc
    if 'www.' in netloc:
        host = netloc.replace('www.', '')
    if ':' in netloc:
        index = netloc.index(':')
        host = netloc[:index]
    return host

def _valid_host(host):
    return WhiteList.query.filter_by(host = host).first()

def _generate_sources(links):
    sources = []
    for link in links:
        source = None
        #make this a function composition
        if _valid_host(_clean_netloc(_get_netloc(link))):
            source = VideoSource(path = link,  length = 120)
        else:
            #ideally use a request head to see content-type
            source = ImageSource(path = link, height = 64, width = 64)
        if source:
            sources.append(source)
    return sources

def create_sources(links):
    sources = _generate_sources(links)
    for source in sources:
        db.session.add(source)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
    return sources


def _generate_meta(message_id, sources):
    return list(map(lambda s: MessageMeta(message_id = message_id, image_id = s.id) if type(s) is ImageSource else MessageMeta(message_id = message_id, video_id = s.id), sources))


def create_metas(message_id, sources):
    metas = _generate_meta(message_id, sources)
    for message_meta in metas:
        db.session.add(message_meta)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
    return metas


def add_user_to_room(user_id, room_id):
    room_user = RoomUser(room_id = room_id, user_id = user_id)
    db.session.add(room_user)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
    finally:
        return room_user

def select_chat_room(rooms, room_id):
    if room_id:
        potential = room_with_id(room_id, rooms)
        if potential:
            return potential
    return rooms[0]


def remove_user_from_room(user_id, room_id):
    ru = user_in_room(user_id, room_id)
    db.session.delete(ru)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return False
    finally:
        return True

#input rooms dicts output room as dictionary
def room_with_id(room_id, rooms):
    for room in rooms:
        if room['id'] == int(room_id):
            return room
    return None
#returns room ids
def unique_rooms(user_ids):
    room_ids = set()
    for user_id in user_ids:
        current_ids = list(map(lambda ru: ru.room_id, get_rooms_by_user(user_id)))
        for room_id in current_ids:
            room_ids.add(room_id)
    return room_ids

#returns room id
def find_room(user_ids):
    room_ids = unique_rooms(user_ids)
    for room_id in room_ids:
        included = list(map(lambda ru: ru.user_id, get_users_by_room(room_id)))
        if included == user_ids:
            return room_id
    return None

def create_user(name, email, password):
    user = User(name = name, email = email, password = password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        sys.stderr.write(e.__doc__)
        return None
        #if commit was successful there will be a user with that id
    finally:
        user = User.query.with_entities(User.id, User.name, User.email).filter_by(email = email).first()
        return user
