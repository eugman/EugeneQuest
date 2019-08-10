from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from trello import TrelloApi

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    player = db.session.query(Player).get(1)

    items = Item.query.all()
    return render_template("shop.html", items = items, player = player)

