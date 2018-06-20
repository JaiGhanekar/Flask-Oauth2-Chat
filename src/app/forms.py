from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required

WTF_CSRF_ENABLED = False

class LoginForm(FlaskForm):
    name = StringField('name', validators=[Required()])
    email = StringField('email', validators=[Required()])
    password = StringField('password', validators=[Required()])