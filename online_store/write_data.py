import csv
import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from online_store.models import Category, Dish, User


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)



#with open('data\delivery_categories.csv', encoding='utf-8') as f:
#    categories = csv.DictReader(f)
#    for row in categories:
#        cat = Category(title=row['title'])
#        db.session.add(cat)
#db.session.commit()


#with open('data\delivery_items.csv', encoding='utf-8') as f:
#    items = csv.DictReader(f)
#    for item in items:
#        dish = Dish(title=item['title'],
#                    price=item['price'],
 #                   description=item['description'],
#                    picture=item['picture'],
#                    category_id=item['category_id']
#                    )
#        db.session.add(dish)
#db.session.commit()


with open('data/users.csv') as f:
    users_data = csv.DictReader(f)
    for data in users_data:
        user_add = User()
        user_add.email = data['email']
        user_add.password_hash = data['password']
        db.session.add(user_add)
db.session.commit()
