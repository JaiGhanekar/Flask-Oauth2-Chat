var base = "http://" + document.domain + ":" + location.port;
$('#login').click(function () {
    var email = $('#email').val();
    var pwd = $('#pwd').val();
    if (email && pwd) {
        var form = new FormData();
        form.append("username", email);
        form.append("password", pwd);
        form.append("client_id", "eG4umCQ3qUTYmQX8SfnkPEbwwGjTOx6TyXifc1FJ");
        form.append("client_secret", "A3hzmToONsEfWp0jWxtk6HWJmvrrC5hT40WPbRwAbNJfZ5E5f0");
        form.append("grant_type", "password");

        var settings = {
            "async": true,
            "crossDomain": true,
            "url": base + "/oauth/token",
            "method": "POST",
            "headers": {
                "Cache-Control": "no-cache",
            },
            "processData": false,
            "contentType": false,
            "mimeType": "multipart/form-data",
            "data": form,
            error: function (request, status, errorThrown) {
                alert("Your email/password combination is wrong");
            }
        }

        $.ajax(settings).done(function (response) {
            data = JSON.parse(response);
            window.location.replace(base + '/chat?access_token=' + data.access_token);
        });
    }
});


$('#signupbtn').click(function () {
    $('#signup').modal('show');
});
$('#close').click(function () {
    $('#signup').modal('hide');
});
$('#savesignupbtn').click(function () {
    var name = $('#signup-name').val();
    var email = $('#signup-email').val();
    var password = $('#signup-pwd').val();
    var form = new FormData();
    form.append("name", name);
    form.append("email", email);
    form.append("password", password);
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": base + "/api/users",
        "method": "POST",
        "headers": {
            "Cache-Control": "no-cache",
        },
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form,
        error: function (request, status, errorThrown) {
            $('#summary').text('Form Error');
        }
    }
    $.ajax(settings).done(function (response) {
        data = JSON.parse(response).result;
        if (data.email) {
            $('#summary').text('Successfully signed up');
            $('#email').val(data.email);
        }
    });
});