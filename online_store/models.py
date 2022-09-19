from werkzeug.security import generate_password_hash, check_password_hash
from online_store import db

from online_store import app

from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user


dish_order_association = db.Table("dish_order",
                                  db.Column("dish_id", db.Integer, db.ForeignKey("dish.id"), unique=False),
                                  db.Column("order_id", db.Integer, db.ForeignKey("orders.id")),
                                  extend_existing=True
                                  )


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')

    orders = db.relationship("Order", back_populates="user")


    @property
    def password_hash(self):
        raise AttributeError('Нет доступа.')

    @password_hash.setter
    def password_hash(self, password_hash):
        self.password = generate_password_hash(password_hash)

    def password_valid(self, password):
        return check_password_hash(self.password, password)


class Dish(db.Model):
    __tablename__ = 'dish'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)

    orders_id = db.relationship("Order", secondary=dish_order_association,
                                back_populates="list_dish", viewonly=False)

    category_id = db.Column(db.Integer, nullable=False)






class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True, default='Гость')
    datetime = db.Column(db.DateTime(timezone=False), default=db.func.now())
    amount = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean)
    mail = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    payment = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("User", back_populates="orders")

    list_dish = db.relationship("Dish", secondary=dish_order_association,
                                back_populates="orders_id", viewonly=False)


# Администратор
admin = Admin(app, template_mode='bootstrap3')
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class AdminCategory(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated



class AdminDish(ModelView):
    form_excluded_columns = ['orders_id']

    def is_accessible(self):
        return current_user.is_authenticated



class AdminUsers(ModelView):
    column_searchable_list = ['email']
    excluded_list_columns = 'password'

    can_delete = False
    can_edit = False
    can_create = False

    def is_accessible(self):
        return current_user.is_authenticated


class AdminOrder(ModelView):
    column_searchable_list = ['name', 'mail', 'datetime']
    column_editable_list = ['status']
    excluded_list_columns = 'user'

    can_create = False


    def is_accessible(self):
        return current_user.is_authenticated


admin.add_link(MenuLink(name='На сайт', url='/'))
admin.add_view(AdminCategory(Category, db.session, 'Категории'))
admin.add_view(AdminDish(Dish, db.session, 'Блюда'))
admin.add_view(AdminUsers(User, db.session, 'Пользователи'))
admin.add_view(AdminOrder(Order, db.session, 'Заказы'))
