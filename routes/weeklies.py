from app import app, db
from app.models import *
from app.config import *
from typing import List

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy


@app.route('/weeklies', methods=['GET', 'POST'])
def weeklies():
    player = db.session.query(Player).get(1)
    player.messages = ""

    hour = datetime.datetime.now().hour
    result = request.form

    if result.get("complete"):
        weekly_id = result.get("weekly_id")
        weekly = db.session.query(weekly).get(weekly_id)   
        weekly.completed = True
        weekly.completedLast = datetime.datetime.now()
        db.session.commit()

        player.messages += addPoints(db, points)


    allweeklies = getQuests("All")

    openweeklies = getQuests("Open")
    
    completedweeklies = getQuests("Completed")
    return render_template("weeklies.html", weeklies = openweeklies, completed = completedweeklies,  player = player)



def getQuests( status:str = "Open") -> List[Weekly]:
    """Takes in types of quests and returns a list of weeklies."""
    hour = datetime.datetime.now().hour
    isWork = 1 if datetime.datetime.today().weekday() in (0, 1, 2, 3, 4) and 9 <= hour < 18 else -1
    query = Weekly.query

    #Filter based on the Status
    if status == "Open":
        query = query.filter_by(completed = False)
    elif status == "Completed":
        query = query.filter_by(completed = True)
    else:
        pass

    weeklies = query.all()
    weeklies = filter(lambda x: x.isWork == 0 or x.isWork == isWork, weeklies)
    
    return list(weeklies)
