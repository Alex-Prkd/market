from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField, SelectField, BooleanField
from flask_wtf import FlaskForm, RecaptchaField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange

from re import search

from online_store import db
from .models import User


class UserData(FlaskForm):
    username = StringField('Ваше имя: ', validators=[Length(min=2),
                                                     InputRequired()])

    address = StringField('Улица:', validators=[InputRequired()])
    home = IntegerField('Дом:', validators=[InputRequired(),
                                            NumberRange(min=1)])
    porch = IntegerField('Подъезд: ', validators=[InputRequired(),
                                                  NumberRange(min=1)])
    flat = IntegerField('Квартира:', validators=[InputRequired(),
                                                 NumberRange(min=1)])
    phone = StringField('Телефон:', default="+375",
                        validators=[Length(min=13, max=13),
                                    InputRequired(message='Все поля обязательный к заполнению')])
    payment = SelectField('Оплата', choices=[('cashless', 'Картой'), ('cash', 'Наличными')])
    submit = SubmitField('Войти')

    @staticmethod
    def is_valid_phone(phone):
        return bool(search(r"(^\+)+(375)+(25|44|33|29)(\d{7})", phone))



class UserLogin(FlaskForm):
    email = EmailField('Эл. почта:', validators=[Length(min=7),
                                                 InputRequired(message='Все поля обязательны к заполнению')])
    password = PasswordField('Пароль:', validators=[Length(min=4),
                                                    InputRequired(message='Все поля обязательный к заполнению')])
    remember = BooleanField('Запомнить')
    recaptcha = RecaptchaField()
    submit = SubmitField('Войти')



class UserRegister(FlaskForm):
    email = EmailField('Эл. почта:', validators=[Length(min=7),
                                                 InputRequired()])
    password = PasswordField('Пароль:', validators=[Length(min=4),
                                                    InputRequired(),
                                                    EqualTo('password_again', message='Пароли не совпадают.')])
    password_again = PasswordField('Повторите пароль:',
                                   validators=[Length(min=4)])
    remember = BooleanField('Запомнить')
    submit = SubmitField('Зарегистроваться')

    @staticmethod
    def is_valid_email(email):
        if db.session.query(User).filter(User.email == email).first():
            return False
        else:
            return True


class ChangeEmail(FlaskForm):
    email_old = EmailField('Старая почта:', validators=[Length(min=7),
                                                        InputRequired()])
    email_new = EmailField('Новая почта:', validators=[Length(min=7),
                                                       InputRequired()])
    password = PasswordField('Пароль:', validators=[Length(min=4),
                                                    InputRequired()])
    submit = SubmitField('Изменить')


class ChangePassword(FlaskForm):
    password = PasswordField('Пароль:', validators=[Length(min=4),
                                                    InputRequired()])
    password_new = PasswordField('Новый пароль:', validators=[Length(min=4),
                                                              InputRequired()])
    submit = SubmitField('Изменить')