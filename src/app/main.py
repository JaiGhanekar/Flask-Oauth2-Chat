from flask import Flask, jsonify, render_template, session
from .auth import oauth
from .models import *
from .utils import *
from .forms import LoginForm

app = Flask(__name__, static_url_path = '/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', defaults={'room_id': None})
@app.route('/chat/<room_id>')
@oauth.require_oauth()
def chat(room_id):
    user = request.oauth.user
    access_token = request.args.get('access_token')
    rus = RoomUser.query.filter_by(user_id = user.id).all()
    rooms = list(map(lambda ru: Room.query.get(ru.room_id).as_dict(),rus))
    if len(rooms) > 0:
        room = select_chat_room(rooms, room_id)
        pagenum = int(request.args.get('pagenum', 1))
        perpage = int(request.args.get('perpage', 2))
        message_pagination = get_messages(room['id'], pagenum, perpage)
        messages = message_pagination.items
        thread = '<br>'.join(list(map(lambda m: m.raw.strip(), messages)))
        return render_template('chat.html', user = request.oauth.user, access_token = access_token, room = room, messages = messages, thread = thread, pages = message_pagination.pages, pagenum = pagenum, perpage = perpage)
    return render_template('chat.html', user = request.oauth.user, access_token = access_token, room = '', messages = '', thread = '', pages = '', pagenum = 1, perpage = 2)

@app.route('/api/rooms', methods = ['POST'])
@oauth.require_oauth()
def new_room():
    user = request.oauth.user
    users = request.form.get('users')
    user_ids = list(map(lambda u: int(u), users.split(',')))
    user_ids.append(user.id)
    user_ids.sort()
    room_id = find_room(user_ids)
    if room_id:
        return jsonify({'result' : room_id}), 201
    else:
        name = user.name + ',' + request.form.get('name')
        room = create_room(name)
        for user_id in user_ids:
            add_user_to_room(user_id, room.id)
        return jsonify({'result' : room.id}), 201

@app.route('/api/rooms', methods = ['GET'])
@oauth.require_oauth()
def get_rooms_api():
    user = request.oauth.user
    rus = get_rooms_by_user(user.id)
    rooms = list(map(lambda ru: Room.query.get(ru.room_id).as_dict(),rus))
    return jsonify({'result' : rooms})

@app.route('/test')
def test():
    return 'Chat is running'

@app.route('/api/me')
@oauth.require_oauth()
def me():
    user = request.oauth.user
    return jsonify({'result' : user.email})

@app.route('/api/users', methods=['GET'])
@oauth.require_oauth()
def get_users():
    users = User.query.with_entities(User.id, User.name, User.email).all()
    response = list(map(lambda user:{'id' : user.id,'name':user.name,'email':user.email},users))
    return jsonify({'result': response})

@app.route('/api/users', methods=['POST'])
def signup():
    form = LoginForm(request.form)
    if form.validate() :
        email = request.form.get("email")
        user = User.query.filter_by(email = email).first()
        if not user:
            name, password = request.form.get('name'), request.form.get('password')
            user = create_user(name, email, password)
            if user:
                return jsonify({"result" : {'id' : user.id,'name':user.name,'email':user.email}}), 201
            else:
                return jsonify({"result" : 'error saving user'}), 400
        else:
            return jsonify({"result" : "email already taken"}), 400
    return jsonify({"result" : "invalid form"}), 400

""" 
    FLASK_OAUTHLIB METHODS 

"""

@app.route('/oauth/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return None

