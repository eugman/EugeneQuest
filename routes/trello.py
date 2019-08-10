from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from trello import TrelloApi



@app.route('/trello', methods=['GET', 'POST'])
def trello():
    result = request.form
    player = db.session.query(Player).get(1)
 
    trello = TrelloApi(TRELLO_KEY)
    trello.set_token(TRELLO_TOKEN)
   

    if result.get("archive"):
        cardid = result.get("id")
        trello.cards.update_closed( cardid, "true")
        addPoints(db, 0.1, "Archived a card")
 
    if result.get("complete"):
        name = result.get("name")
        m = re.search("\((.+)\)", name)
        if m:
            points = float(m.group(1))
        else:
            points = float("0.25")

        addPoints(db, points, "Trello task: "+name)
        cardid = result.get("id")
        cardGrouping  = result.get("grouping")
        
        if cardGrouping == "Home":
            done = HOME_DONE_LIST
        else:
            done = WORK_DONE_LIST

        trello.cards.update_idList(cardid, done)
 
    homeCards = trello.lists.get_card(HOME_WEEK_LIST)
    workCards = trello.lists.get_card(WORK_WEEK_LIST)

    doneCards = trello.lists.get_card(HOME_DONE_LIST)
    doneCards += trello.lists.get_card(WORK_DONE_LIST)

    for card in homeCards:
        card["grouping"] = "Home"
    for card in workCards:
        card["grouping"] = "Work"

    if not datetime.datetime.today().weekday in (5,6) and 9 <= datetime.datetime.now().hour <= 18:
        cards = homeCards + workCards
    else:
        cards = homeCards

    for card in cards:

        m = re.search("\((.+)\)", card["name"])
        if m:
            card["points"] = float(m.group(1))
        else:
            card["points"] = 0.25

    cards = sorted(cards, key = lambda c: c["points"])
    doneCards = sorted(doneCards, key=lambda c: c["dateLastActivity"], reverse = True)
    return render_template("trello.html",cards = cards, doneCards = doneCards, player = player)

