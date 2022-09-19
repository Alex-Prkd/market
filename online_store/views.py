from flask import render_template, request, session, redirect, url_for, abort, flash, make_response
from flask_login import login_user, logout_user
from sqlalchemy import func

from hashlib import sha256

from online_store import app, db
from .models import User, Dish, Category, Order, dish_order_association
from .forms import UserData, UserLogin, UserRegister, ChangeEmail, ChangePassword


def create_session_user(user):
    session['user'] = {
        'user_id': user.id,
        'user_email': user.email,
        'user_role': user.role
    }


def create_remember_me_cookie(user):
    max_age = 20*100
    create_session_user(user)
    value = f'{user.email}:{user.password}:{max_age}:{user.id}'
    cookie_hash = sha256(value.encode()).hexdigest()
    res = make_response(redirect('/'))
    res.set_cookie('remember', str(f'{cookie_hash}:{user.email}:{max_age}'), max_age)
    return res


def valid_cookie():
    try:
        if request.cookies.get('remember'):
            cookie_data = request.cookies.get('remember').split(':')
            value_cookie = cookie_data[0]
            email_cookie = cookie_data[1]
            age_cookie = cookie_data[2]
            user = db.session.query(User).filter(User.email == email_cookie).first()
            if user:
                check_cookie = f'{email_cookie}:{user.password}:{age_cookie}:{user.id}'
                check_hash = sha256(check_cookie.encode()).hexdigest()
                if check_hash == value_cookie:
                    if not session['user']:
                        create_session_user(user)
                    return True
                else:
                    return abort(404)
            else:
                return abort(404)
        # удалили данные
        res = make_response()
        res.set_cookie('remember', max_age=0)
    # удалили часть данных
    except IndexError:
        res = make_response()
        res.set_cookie('remember', max_age=0)



def add_to_cart_func(booking):
    db_food = {}
    amount_dish = 0
    sum_price = 0
    for food_id, amount in booking.items():
        amount_dish += amount
        dish = Dish.query.get(food_id)
        db_food[dish] = amount
        sum_price += int(dish.price) * amount
    session['header'] = sum_price
    return db_food, amount_dish, sum_price


@app.route('/', methods=["POST", "GET"])
def index():
    valid_cookie()
    categories = Category.query.order_by(Category.id).all()
    category_and_food = {}
    for category in categories:
        food = Dish.query.filter(Dish.category_id == category.id).all()
        category_and_food.update({category: food})
    return render_template('main.html',
                           categories=category_and_food,
                           title="Главная",
                           header=session.get('header', None),
                           user_active=session.get('user')
                           )


@app.route('/addtocart/', methods=["POST"])
def add_to_cart():
    if request.method == "POST":
        id = int(request.form['product_id'])
        selected_food = Dish.query.get_or_404(id)
        if selected_food:
            order = session.get('cart', {})
            order[str(id)] = order.get(str(id), 0) + 1
            session['cart'] = order
            add_to_cart_func(order)
            return redirect('/')
    return abort(404)


@app.route('/cart/', methods=["POST", "GET"])
def cart():
    valid_cookie()
    booking = session.get('cart', {})
    form = UserData()
    if not form.validate_on_submit():
        db_food, amount_dish, sum_price = add_to_cart_func(booking)
        return render_template('cart.html',
                               db_food=db_food,
                               amount_dish=amount_dish,
                               sum_price=sum_price,
                               form=form,
                               title="Корзина",
                               header=session.get('header'),
                               user_active=session.get('user')
                               )

    # Валидация номера forms.py->UserData->is_valid_phone
    if UserData.is_valid_phone(phone=form.phone.data):
        address = f'ул. {form.address.data} д. {form.home.data} п. {form.porch.data} кв. {form.flat.data}'
        order = Order(
            name=form.username.data,
            amount=request.form['sum_price'],
            status=True,
            mail=session['user']['user_email'],
            phone=form.phone.data,
            address=address,
            user_id=session['user']['user_id'],
            payment=form.payment.data
            )
        db.session.add(order)
        for food_id, amount in booking.items():
            dish = db.session.query(Dish).get(food_id)
            for num in range(amount):
                order.list_dish.append(dish)
        db.session.commit()
        return redirect('/ordered/', code=307)
    else:
        flash('Номер введён некорректно.')
        return redirect('/cart/')


@app.route('/ordered/', methods=['POST'])
def ordered():
    if session.get('cart'):
        del session['cart']
    if session.get('header'):
        del session['header']
    return render_template('ordered.html',
                           id=session['user']['user_id']
                           )


@app.route('/account/<int:id>/', methods=['GET', 'POST'])
def account(id):
    valid_cookie()
    if not session.get('user'):
        return redirect('/login/')
    if session['user']['user_id'] != id:
        abort(404)
    num_active_order = 0
    orders = db.session.query(Order).filter(Order.user_id == id).order_by(Order.datetime.desc()).all()
    order_and_dish = {}

    for order in orders:
        if order.status:
            num_active_order += 1
        order_and_dish[order] = []
        for dish in order.list_dish:
            quantity_dish = db.session.query(func.count(dish_order_association.c.dish_id))\
                .join(Dish, Order)\
                .filter(Order.id == order.id)\
                .filter(Dish.id == dish.id)\
                .scalar()
            order_and_dish[order].append({dish: quantity_dish})
    return render_template('account.html',
                           header=session.get('header'),
                           orders=order_and_dish,
                           num_active_order=num_active_order,
                           user_active=session.get('user')
                           )


@app.route('/delete_dish/<int:id>/', methods=['GET', 'POST'])
def delete_dish(id):
    order = session.get('cart')
    order.pop(str(id))
    session['cart'] = order
    flash('Блюдо удалено из корзины.')
    return redirect(url_for('cart'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        return redirect('/')
    form = UserRegister()
    if form.validate_on_submit():
        # проверка уникальности почты forms.py -> UserRegister -> is_valid_email
        if not UserRegister.is_valid_email(form.email.data):
            flash('Аккаунт с такой почтой зарегистрирован.')
            return redirect('/register/')
        register_user = User()
        register_user.email = form.email.data
        register_user.password_hash = form.password.data
        db.session.add(register_user)
        db.session.commit()

        user = db.session.query(User).filter(User.email == form.email.data).first()
        session['user'] = {
            'user_id': user.id,
            'user_email': user.email,
            'user_role': user.role
                           }
        if form.remember.data:
            res = create_remember_me_cookie(user)
            return res
        return redirect('/')
    return render_template('register.html',
                           form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect('/')
    form_auth = UserLogin()
    if form_auth.validate_on_submit():
        user = User.query.filter(User.email == form_auth.email.data).first()
        if user and user.password_valid(form_auth.password.data):
            if user.role == 'admin':
                login_user(user)
            if form_auth.remember.data:
                res = create_remember_me_cookie(user)
                return res
            create_session_user(user)
            return redirect('/')
        else:
            if not user:
                flash('Аккаунт не найден.')
            else:
                flash('Неправильный пароль.')
            return redirect('/login/')
    return render_template('auth.html',
                           form_auth=form_auth)


@app.route('/logout/', methods=["GET", "POST"])
def logout():
    if session.get('cart'):
        del session['cart']
    if session.get('header'):
        del session['header']
    if session.get('user'):
        del session['user']
    res = make_response(redirect('/'))
    res.set_cookie('remember', max_age=0)
    logout_user()
    return res


@app.route('/settings/account/<int:id>/', methods=['POST', 'GET'])
def settings(id):
    try:
        valid_cookie()
        if id != session['user']['user_id']:
            abort(404, 'err')
        user_active = session.get('user')
        header = session.get('header')
        if request.method == 'POST':
            if request.form['value'] == 'email':
                return redirect('/change_email/', code=307)
            elif request.form['value'] == 'password':
                return redirect('/change_password/', code=307)
        return render_template('settings.html',
                               user_active=user_active,
                               header=header
                               )
    except KeyError:
        abort(404)


@app.route('/change_email/', methods=['POST'])
def change_email():
    user_active = session.get('user')
    user = db.session.query(User).get(user_active['user_id'])
    form = ChangeEmail()
    if not form.validate_on_submit():
        return render_template('change_email.html',
                               user_active=user_active,
                               form=form
                               )

    if user.password_valid(form.password.data) and user.email == form.email_old.data:
        new_email = form.email_new.data
        user_active['user_email'] = new_email
        user.email = new_email
        db.session.add(user)
        db.session.commit()
        flash('Почта изменена.')
        return render_template('settings.html',
                               user_active=user_active)
    else:
        flash('Ошибка! Проверьте вводимые данные.')
        return render_template('settings.html',
                               user_active=user_active)


@app.route('/change_password/', methods=['POST'])
def change_password():
    user_active = session.get('user')
    user = db.session.query(User).get(user_active['user_id'])
    form = ChangePassword()
    if not form.validate_on_submit():
        return render_template('change_password.html',
                               user_active=user_active,
                               form=form
                               )

    if user.password_valid(form.password.data):
        new_password = form.password_new.data
        user.password_hash = new_password
        db.session.add(user)
        db.session.commit()
        flash('Пароль изменен.')
        return render_template('settings.html',
                               user_active=user_active)
    else:
        flash('Ошибка! Проверьте вводимые данные.')
        return render_template('settings.html',
                               user_active=user_active)



@app.errorhandler(404)
def err_html(err):
    user_active = session.get('user')
    return render_template('err.html',
                           err=err,
                           user_active=user_active
                           )