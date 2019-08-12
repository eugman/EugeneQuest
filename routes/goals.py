from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy


@app.route('/goals', methods=['GET', 'POST'])
def goals():
    player = db.session.query(Player).get(1)
    result = request.form

    if result.get("id"):
        goal_id = int(result.get("id"))
        goal = db.session.query(Goal).get(goal_id)
        goal.current = int(result.get("current"))

        db.session.commit()

    goals = Goal.query.all()
    goals = sorted(goals, key = lambda x: float(x.level()), reverse = True)
    return render_template("goals.html", goals = goals, player = player)

