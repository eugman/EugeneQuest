from app import app, db
from app.models import *
from app.config import *
import re
from typing import List

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy



@app.route('/add', methods=['GET', 'POST'])
def add():
    player = db.session.query(Player).get(1)
    result = request.form

    if result.get("new_daily"):
        db.session.add(Daily(name=result.get("new_daily")))
        db.session.commit()

    return render_template("add.html", player = player)



@app.route('/', methods=['GET', 'POST'])
def index():
    player = db.session.query(Player).get(1)
    player.messages = ""

    hour = datetime.datetime.now().hour
    result = request.form

    if result.get("bookid") and result.get("page"):
        book_id = result.get("bookid")
        book = db.session.query(Book).get(book_id)
        book.page = int(result.get("page"))
        db.session.commit()

    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        daily.completedLast = datetime.datetime.now()
        daily.rest = daily.restDuration
        db.session.commit()

        player.messages += addPoints(db, daily.totalPoints())

        if result.get("bg"):
            if 80 < int(result.get("bg")) < 140:
               player.messages += addPoints(db, 5)
            db.session.add(BG(BG=result.get("bg"), insulin=result.get("insulin")))
            db.session.commit()

        if result.get("bookid") and result.get("page"):
            book_id = result.get("bookid")
            book = db.session.query(Book).get(book_id)
            book.page = int(result.get("page"))
            db.session.commit()



    if result.get("snooze_daily"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.snooze = hour + 2
        db.session.commit()
        print(hour)

    if result.get("reset_dailies"):
        Daily.query.update({Daily.completed: False})
        db.session.commit()
        
    books = Book.query.all()       

    isWork = 0 if datetime.datetime.today().weekday in (5, 6) else 1

    allDailies = Daily.query.filter(Daily.subtype != "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).all()
    stats = DailyStats(allDailies)

    openDailies = getQuests("Main", "Open")
    
    
    openSideQuests = getQuests("Side", "Open", 0)
    
    if len(openSideQuests) == 0:
        openSideQuests = getQuests("Side", "Open", 1)
    
    completedDailies = getQuests("Main", "Completed")
    missedDailies = getQuests("Main", "Missed")
    return render_template("index.html", dailies = openDailies, completed = completedDailies, missed = missedDailies, sideQuests = openSideQuests, stats = stats, player = player, books = books)



def getQuests(subtype:str = "Main", status:str = "Open", sideQuestRest:int = 0) -> List[Daily]:
    """Takes in types of quests and returns a list of dailies."""
    hour = datetime.datetime.now().hour
    isWork = datetime.datetime.today().weekday in (5, 6)
    query = Daily.query

    if subtype == "Main":
        query = query.filter(Daily.subtype != "Side")
    else:
        query = query.filter(Daily.subtype == "Side", Daily.rest <= sideQuestRest)

    if status == "Open":
        query = query.filter_by(completed = False).filter(Daily.availableAfter <= hour, Daily.availableUntil > hour, Daily.snooze < hour)
        if subtype == "Main":
            query = query.order_by(Daily.points.desc(), "availableAfter", "availableUntil")
        else:
            query = query.order_by("rest", Daily.points.desc())
    elif status == "Missed":
        query = query.filter_by(completed = False).filter(hour >= Daily.availableUntil)
        query = query.order_by("availableAfter", "availableUntil")
    else:
        query = query.filter_by(completed = True)
        query = query.order_by("availableAfter", "availableUntil")

    dailies = query.all()
    dailies = filter(lambda x: x.isWork == False or x.isWork == isWork, dailies)
    
    return list(dailies)
