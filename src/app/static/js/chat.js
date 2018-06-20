var socket;
var base = 'http://' + document.domain + ':' + location.port;
perpage = parseInt(perpage, 10);
pagenum = parseInt(pagenum, 10);

$(document).ready(function () {
    get_conversations();
    initialize();
    get_users();
    pager();
    modals();
    sockets();

});

function sockets() {
    socket = io.connect(base + '/chat');
    socket.on('connect', function () {
      socket.emit('joined', {
            'room_id': room_id,
            'username': username
        });
    });
    socket.on('status', function (data) {
        if ($('#chat').val().indexOf('<' + data.msg + '>\n') == -1) {
            $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        }
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    socket.on('message', function (data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    $('#text').keypress(function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            socket.emit('text', {
                msg: text,
                'room_id': room_id,
                'username': username,
                'user_id': user_id,
                'sent_at': new Date().toJSON()
            });
        }
    });
}

function pager() {
    var numpages = parseInt(pages, 10);
    $('#next').click(function () {
        if (pagenum + 1 <= numpages) {
            var value = pagenum + 1;
            window.location.replace(base + '/chat/' + room_id + '?access_token=' + access_token + '&pagenum=' + value + '&perpage=' + perpage);
        }
        else {
            $('#previous').prop("disabled", false);
            $('#next').prop("disabled", true);
        }
    });
    $('#previous').click(function () {
        if (pagenum - 1 >= 1) {
            var value = pagenum - 1;
            window.location.replace(base + '/chat/' + room_id + '?access_token=' + access_token + '&pagenum=' + value + '&perpage=' + perpage);
        }
        else {
            $('#next').prop("disabled", false);
            $('#previous').prop("disabled", true);
        }
    });
}

function initialize() {
    $('#chat').val('');
    if (message_thread) {
        var values = message_thread.split('&lt;br&gt;');
        for (var i = 0; i < values.length; i++) {
            $('#chat').val($('#chat').val() + $.trim(values[i]) + '\n');
        }
        $('#chat').val($('#chat').val() + 'pg. ' + pagenum + '\n');
    }
}

function modals() {
    $('#settingbtn').click(function () {
        $('#settings').modal('show');
    });
    $('#close').click(function () {
        if (room_id) {
            $('#settings').modal('hide');
        }
        else {
            $('#close').prop("disabled", true);
        }

    });
    $('#savesettingbtn').click(function () {
        var name = extract_option_text();
        var values = extract_options_val();
        if (values) {
            switch_context(name, values);
        }
        if (room_id && !values) {
            perpage = $('#perpage').val();
            $('#settings').modal('hide');
            window.location.replace(base + '/chat/' + room_id + '?access_token=' + access_token + '&pagenum=1' + '&perpage=' + perpage);
        }

    });
}

function switch_context(name, values) {
    var form = new FormData();
    form.append("users", values);
    form.append("name", name);
    form.append("access_token", access_token);
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": base + "/api/rooms",
        "method": "POST",
        "headers": {
            "Cache-Control": "no-cache",
        },
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form
    }

    $.ajax(settings).done(function (response) {
        data = JSON.parse(response);
        window.location.replace(base + '/chat/' + data.result + '?access_token=' + access_token + '&pagenum=1' + '&perpage=' + perpage);
    });
}

function leave_room() {
    socket.emit('left', {
        'room_id': room_id,
        'username': username,
        'user_id': user_id
    }, function () {
        socket.disconnect();
    });
    window.location.replace(base + '/chat?access_token=' + access_token);
}

function logout() {
    window.location.replace(base);
}

function extract_option_text() {
    return $('#users option:selected').map(function () {
        return $(this).text();
    }).get().join();
}

function extract_options_val() {
    return $('#users option:selected').map(function () {
        return $(this).val();
    }).get().join();
}

function get_users() {
    var options = '';
    $.get(base + '/api/users?access_token=' + access_token, function (data) {
        result = data.result;
        for (var i = 0; i < result.length; i++) {
            if (result[i].id != user_id) {
                options += '<option value="' + result[i].id + "\"" + '>' + result[i].name + '</option>'
            }
        }
        $('#users').append(options);
    });
}

function get_conversations() {
    $.get(base + '/api/rooms?access_token=' + access_token, function (data) {
        var rooms = data.result;
        if (rooms.length > 0) {
            conversation_html(rooms);
        }
        else {
            $('#settings').modal('show');
        }

    });
}

function conversation_html(rooms) {
    var conversations = '';
    for (var i = 0; i < rooms.length; i++) {
        href = '/chat/' + rooms[i].id + "?access_token=" + access_token;
        conversations += '<tr><td><a href="' + href + "\"" + '>' + rooms[i].name + '</a></td></tr>';
    }
    $('#conversations').append(conversations);
}