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
        page = int(result.get("page"))
        book.current = page
        if page >= book.pages:
            book.completed = True
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
        daily.snooze = hour + int(result.get("snooze_daily"))
        db.session.commit()
        print(hour)

    if result.get("reset_dailies"):
        Daily.query.update({Daily.completed: False})
        db.session.commit()
        
    books = Book.query.all()       

    vacation = player.vacation
    print(vacation)


    allDailies = getQuests(vacation, "Main", "All")
    stats = DailyStats(allDailies)

    openDailies = getQuests(vacation, "Main", "Open")
    
    
    openSideQuests = getQuests(vacation, "Side", "Open",  0)
    
    if len(openSideQuests) == 0:
        openSideQuests = getQuests(vacation, "Side", "Open",  1) + getQuests(vacation, "Bonus","Open", 0) 

        if len(openSideQuests) == 0:
            openSideQuests = getQuests(vacation, "Bonus", "Open", 1)
    
    completedDailies = getQuests(vacation, "Main", "Completed")
    missedDailies = getQuests(vacation, "Main", "Missed")
    return render_template("index.html", dailies = openDailies, completed = completedDailies, missed = missedDailies, sideQuests = openSideQuests, stats = stats, player = player, books = books)



def getQuests(vacation:int, subtype:str = "Main", status:str = "Open", sideQuestRest:int = 0) -> List[Daily]:
    """Takes in types of quests and returns a list of dailies."""
    hour = datetime.datetime.now().hour
    isWork = 1 if datetime.datetime.today().weekday() in (0, 1, 2, 3, 4) and 9 <= hour < 18 and hour != 12 else -1
    query = Daily.query

    #Filter based on the category of quest
    if subtype == "Main":
        query = query.filter(Daily.subtype != "Side", Daily.subtype != "Bonus")
    elif subtype == "Side":
        query = query.filter(Daily.subtype == "Side", Daily.rest <= sideQuestRest)
    else:
        query = query.filter(Daily.subtype == "Bonus", Daily.rest <= sideQuestRest)

#Filter based on the Status
    if status == "Open":
        query = query.filter_by(completed = False).filter(Daily.availableAfter <= hour, Daily.availableUntil > hour, Daily.snooze < hour)
        if subtype == "Main":
            query = query.order_by(Daily.points.desc(), "availableAfter", "availableUntil")
        else:
            query = query.order_by("rest", Daily.points.desc(), "completedLast")
    elif status == "Missed":
        query = query.filter_by(completed = False).filter(hour >= Daily.availableUntil)
        query = query.order_by("availableAfter", "availableUntil")
    elif status == "Completed":
        query = query.filter_by(completed = True)
        query = query.order_by("availableAfter", "availableUntil")
    else:
        pass

    dailies = query.all()
    dailies = list(filter(lambda x: x.isWork == 0 or x.isWork == isWork, dailies))
    dailies = list(filter(lambda x: x.vacation == 0 or x.vacation == vacation, dailies))
    
    return list(dailies)
