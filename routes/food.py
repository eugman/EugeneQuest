from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy



@app.route('/food', methods=['GET', 'POST'])
def food():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("logfood"):
        if result.get("food_id"):
            food = Food.query.get(result.get("food_id"))
            name = food.name
            carbs = food.carbs



        else:
            name = result.get("name")
            carbs = int(result.get("carbs") or 0)


        db.session.add(FoodLog(name=name,carbs =carbs))
        db.session.commit()

        addPoints(db, 1)


    foods = Food.query.all()
    logs = FoodLog.query.filter(FoodLog.when >= datetime.datetime.combine(datetime.datetime.today(), datetime.time())).all()

    stats = FoodStats(logs)

    return render_template("food.html", logs=logs, stats=stats, foods = foods, player = player)

