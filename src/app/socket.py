from flask import session
from flask_socketio import emit, join_room, leave_room
import sys
from flask_socketio import SocketIO
from .utils import *
socketio = SocketIO()
@socketio.on('joined', namespace='/chat')
def joined(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room_id = data.get('room_id')
    username = data.get('username', '')
    join_room(room_id)
    emit('status', {'msg': username + ' has entered the room.'}, room=room_id)


@socketio.on('text', namespace='/chat')
def text(data):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room_id = data.get('room_id')
    username = data.get('username')
    user_id = data.get('user_id')
    sent_at = data.get('sent_at')
    raw =  '@' + username + ': ' + data['msg']  + ' | ' +  sent_at
    message = create_message(user_id, room_id, raw)
    links = parse_links(raw)
    if len(links) > 0:
        sources = create_sources(links)
        metas = create_metas(message.id, sources)
        res = list(map(lambda s: str(s), sources))
        emit('message', {'msg': username + ' created new sources of type: ' + str(res)}, room=room_id)
    emit('message', {'msg': raw}, room=room_id)


@socketio.on('left', namespace='/chat')
def left(data):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username', '')
    remove_user_from_room(user_id, room_id)
    leave_room(room_id)
    emit('status', {'msg':username + ' has left the room.'}, room=room_id)
