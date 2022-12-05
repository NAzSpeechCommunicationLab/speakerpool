from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SubmitField, PasswordField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from SpeakerPool.models import Account
import json

# length = ""
# username_taken = ""
# print(lang)
# with open(r"SpeakerPool/static/translations.json", "r") as translations_file:
#     translations = json.load(translations_file)
#     length = translations['length'][lang]
#     username_taken = translations['usernametaken'][lang]


class ConsentForm(FlaskForm):
    agree = SubmitField('I Agree')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=20, message="length error")])
    password = PasswordField('Password', validators=[Length(min=4, max=20, message="length error")])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message="equal error")])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = Account.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("username taken")
        if " " in username.data:
            raise ValidationError("space error")

    # def validate_space(self, username):
    #     if " " in username.data:
    #         raise ValidationError("space error")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=20, message="length error")])
    password = PasswordField('Password', validators=[Length(min=4, max=20, message="password length error")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EmailForm(FlaskForm):
    email = StringField('Email',validators=[Email(message="email error")])
    submit = SubmitField('Submit')