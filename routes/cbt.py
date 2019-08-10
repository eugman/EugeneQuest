from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from trello import TrelloApi


@app.route('/cbt', methods=['GET', 'POST'])
def CBT_route():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("neg"):
        neg = int(result.get("neg"))
        player.negThoughts += neg
        db.session.commit()
        if result.get("distortion"):
            addPoints(db, 0.2 * neg)
        else:
            addPoints(db, 0.1 * neg)
 
    if result.get("CBT"):
        A = result.get("A")
        B = result.get("B")
        C = result.get("C")
        D = result.get("D")
        E = result.get("E")

        db.session.add(CBT(A=A, B=B, C=C, D=D, E=E))
        
        db.session.commit()

        addPoints(db, 1)
    

    CBTs = []
    return render_template("cbt.html", CBTs = CBTs, player = player)

