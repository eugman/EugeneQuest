from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy


@app.route('/bg', methods=['GET', 'POST'])
def BG_route():
    player = db.session.query(Player).get(1)

    BGs = BG.query.order_by(BG.when.desc()).all()
    return render_template("bg.html", BGs = BGs, player = player)

