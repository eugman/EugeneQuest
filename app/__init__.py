import sys

if sys.version_info[0] < 3:
    print("Wrong version of python!")
    exit()

import os
from decimal import Decimal
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

template_dir = '../templates'

app = Flask(__name__, template_folder = template_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def addPoints(db, points: Decimal, message: str = "No message set") -> None:
    player = db.session.query(Player).get(1)   
    player.points += points
    db.session.commit()

    db.session.add(PointsLog(points=points, message = message))
    db.session.commit()

from app import models
from routes import *


