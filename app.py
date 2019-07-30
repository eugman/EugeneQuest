import sys

if sys.version_info[0] < 3:
    print("Wrong version of python!")
    exit()

import datetime
import re
from decimal import Decimal
from config import *
from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from trello import TrelloApi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def addPoints(db, points: Decimal, message: str = "No message set") -> None:
    player = db.session.query(Player).get(1)   
    player.points += points
    db.session.commit()


    db.session.add(PointsLog(points=points, message = message))
    db.session.commit()



#########################################################
#                         Models                        #
#########################################################
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Numeric)
    goal = db.Column(db.Integer, default = 700)
    negThoughts = db.Column(db.Integer, default = 0)
    CBTs = db.Column(db.Integer, default = 0)

    def cash(self) -> str:
        return '${:,.2f}'.format(self.points / 100)

    def percent(self) -> str:
        return '{:,.2f}%'.format(100 * self.points / self.goal)

class CBT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    A = db.Column(db.String,  nullable = False)
    B = db.Column(db.String,  nullable = False)
    C = db.Column(db.String,  nullable = False)
    D = db.Column(db.String,  nullable = False)
    E = db.Column(db.String,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)



class BG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    BG = db.Column(db.Integer,  nullable = False)
    insulin = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

    def color(self) -> str:
        if 80 < self.BG < 120:
            return "table-success"
        elif self.BG <= 160:
            return "table-warning"
        else:
            return "table-danger"

class WeightLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

class PointsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Numeric,  nullable = False)
    message = db.Column(db.String,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer,  nullable = False)
    cost = db.Column(db.Integer, nullable=False)
    purchased = db.Column(db.Boolean, default=False)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    carbs = db.Column(db.Integer,  nullable = False)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    carbs = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

class Boardgame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    lastPlayed = db.Column(db.DateTime)
    minPlayers = db.Column(db.Integer,  nullable = False)
    maxPlayers = db.Column(db.Integer,  nullable = False)
    #boardgame subcategory / expansion ???
    eugeneRating = db.Column(db.Integer)
    annieRating = db.Column(db.Integer)
    #isCoop
    #Player type: 2 player, 3-5, party
    #    bggid
    #play time
    #iswallofshame
    #genre - eurogame, ameritash, party game

class BoardgameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    boardgame_id = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)
    notes = db.Column(db.String)
    no_players = db.Column(db.Integer,  nullable = False)
    #winner
    #eugenepoints
    #annie points



class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    subtype = db.Column(db.String, nullable = True)
    availableAfter = db.Column(db.Integer, nullable = False, default = 0)
    availableUntil = db.Column(db.Integer, nullable = False, default = 24)
    completed = db.Column(db.Boolean, default = False, nullable = False)
    completedLast = db.Column(db.DateTime)
    points = db.Column(db.Integer, nullable = False, default = 0)

    def json(self):
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    reps = db.Column(db.Integer, default = 1)
    sets = db.Column(db.Integer, default = 1)
    weight = db.Column(db.Integer, default = 0)
    vest = db.Column(db.Boolean, default = False)
    completed = db.Column(db.Boolean, default = False)

    def json(self) -> str:
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

#########################################################
#                          Stats                        #
#########################################################


class DailyStats():
    def __init__(self, dailies):
        hour = datetime.datetime.now().hour
        self.completedCount = len(list(filter(lambda x: (x.completed == True), dailies)))
        self.missedCount =  len(list(filter(lambda x: (x.completed == False and hour > x.availableUntil), dailies)))
        self.availableCount =  len(list(filter(lambda x: (hour >= x.availableAfter), dailies)))
        self.questCount = self.availableCount + self.missedCount
        self.completedPercent = str(int(100.0 * self.completedCount / self.availableCount))
        self.missedPercent = str(int(100.0 * self.missedCount / self.availableCount))

class FoodStats():
    def __init__(self, foodLogs):
        self.carbs = 0
        self.max = 135
        for log in foodLogs:
            self.carbs += log.carbs

        hour = datetime.datetime.now().hour

        if hour <= 10:
            thirds = 1
        elif hour <= 16:
            thirds = 2
        else:
            thirds = 3

        self.percent = int(100 * self.carbs / self.max)
        #Prorated percent of carbs based on part of day.
        self.curPercent = int(100 * self.carbs / (self.max * thirds / 3))

        if self.curPercent <= 90:
            self.color = "bg-success"
        elif self.curPercent <= 112:
            self.color = "bg-warning"
        else:
            self.color = "bg-danger"

#########################################################
#                         Routes                        #
#########################################################



@app.route('/api/openquests')
def openquests():
    output = "["
    hour = datetime.datetime.now().hour
    openDailies = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).order_by("availableAfter", "availableUntil").all()

    if len(openDailies) == 0:
        output += "]"
    else:
        for daily in openDailies:
            output += daily.json() + ',\n'

        output = output[:-2] + "]"

    return Response(output, mimetype='application/json')


@app.route('/add', methods=['GET', 'POST'])
def add():
    result = request.form

    if result.get("new_daily"):
        db.session.add(Daily(name=result.get("new_daily")))
        db.session.commit()

    return render_template("add.html")

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

@app.route('/cbt', methods=['GET', 'POST'])
def CBT_route():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("neg"):
        player.negThoughts +=1
        db.session.commit()
        if result.get("distortion"):
            addPoints(db, Decimal(0.2))
        else:
            addPoints(db, Decimal(0.1))
 
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

@app.route('/bg', methods=['GET', 'POST'])
def BG_route():
    player = db.session.query(Player).get(1)

    BGs = BG.query.order_by(BG.when.desc()).all()
    return render_template("bg.html", BGs = BGs, player = player)

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    player = db.session.query(Player).get(1)

    items = Item.query.all()
    return render_template("shop.html", items = items, player = player)

@app.route('/trello', methods=['GET', 'POST'])
def trello():
    result = request.form
    player = db.session.query(Player).get(1)
 
    trello = TrelloApi(TRELLO_KEY)
    trello.set_token(TRELLO_TOKEN)
    
    if result.get("complete"):
        name = result.get("name")
        m = re.search("\((.+)\)", name)
        if m:
            points = Decimal(m.group(1))
        else:
            points = Decimal("0.25")

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

    for card in homeCards:
        card["grouping"] = "Home"
    for card in workCards:
        card["grouping"] = "Work"

    cards = homeCards + workCards

    for card in cards:

        m = re.search("\((.+)\)", card["name"])
        if m:
            card["points"] = float(m.group(1))
        else:
            card["points"] = 0.25

    cards = sorted(cards, key = lambda c: c["points"])
    return render_template("trello.html",cards = cards, player = player)

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("increase"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        
        if exercise.name in ["Jumping jacks", "Wall sit", "Plank"]:
            reps = 5
        else:
            reps = 1
        
        exercise.completed = True
        exercise.lastCompleted = datetime.datetime.now()
        exercise.reps += reps
        db.session.commit()

        addPoints(db, 2)

    if result.get("same"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        exercise.completed = True
        exercise.lastCompleted = datetime.datetime.now()
        db.session.commit()

        addPoints(db, 1)
    if result.get("decrease"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        if exercise.name in ["Jumping jacks", "Wall sit", "Plank"]:
            reps = 5
        else:
            reps = 1
        exercise.completed = True
        exercise.lastCompleted = datetime.datetime.now()
        exercise.reps -= reps
        db.session.commit()

        addPoints(db, 1)




    allExercises = Exercise.query.all()

    return render_template("exercise.html", exercises = allExercises, player = player)


@app.route('/', methods=['GET', 'POST'])
def index():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        db.session.commit()

        addPoints(db, daily.points)

        if result.get("bg"):
            if 80 < int(result.get("bg")) < 140:
                addPoints(db, 5)
            db.session.add(BG(BG=result.get("bg"), insulin=result.get("insulin")))
            db.session.commit()


    if result.get("delete_daily"):
        daily_id = result.get("daily_id")
        Daily.query.filter_by(id = daily_id).delete()
        db.session.commit()

    if result.get("reset_dailies"):
        Daily.query.update({Daily.completed: False})
        db.session.commit()
        
       
    hour = datetime.datetime.now().hour

    allDailies = Daily.query.all()
    stats = DailyStats(allDailies)

    openDailies = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).order_by(Daily.points.desc(), "availableAfter", "availableUntil").all()
    completedDailies = Daily.query.filter_by(completed=True).order_by("availableAfter", "availableUntil").all()
    missedDailies = Daily.query.filter_by(completed=False).filter(hour > Daily.availableUntil).order_by("availableAfter", "availableUntil").all()

    return render_template("index.html", dailies = openDailies, completed = completedDailies, missed = missedDailies, stats = stats, player = player)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = PORT)

