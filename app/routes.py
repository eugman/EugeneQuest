from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from trello import TrelloApi



@app.route('/add', methods=['GET', 'POST'])
def add():
    player = db.session.query(Player).get(1)
    result = request.form

    if result.get("new_daily"):
        db.session.add(Daily(name=result.get("new_daily")))
        db.session.commit()

    return render_template("add.html", player = player)



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
        neg = int(result.get("neg"))
        player.negThoughts += neg
        db.session.commit()
        if result.get("distortion"):
            addPoints(db, Decimal(0.2) * neg)
        else:
            addPoints(db, Decimal(0.1) * neg)
 
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

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    player = db.session.query(Player).get(1)

    goals = Goal.query.all()
    return render_template("goals.html", goals = goals, player = player)


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

@app.route('/toggl', methods=['GET', 'POST'])
def toggle():
    result = request.form
    player = db.session.query(Player).get(1)
 
    toggl_client = TogglClientApi(toggleSettings)
    
    workspaces = toggl_client.get_workspaces()

    print(workspaces)
    return render_template("toggl.html", player = player)


@app.route('/trello', methods=['GET', 'POST'])
def trello():
    result = request.form
    player = db.session.query(Player).get(1)
 
    trello = TrelloApi(TRELLO_KEY)
    trello.set_token(TRELLO_TOKEN)
   

    if result.get("archive"):
        cardid = result.get("id")
        trello.cards.update_closed( cardid, "true")
        addPoints(db, Decimal(0.1), "Archived a card")

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

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("increase"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.reps += exercise.interval
        exercise.rest = 3
        db.session.commit()

        addPoints(db, 2)

    if result.get("same"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.rest = 2
        db.session.commit()

        addPoints(db, 1)
    if result.get("decrease"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.reps -= exercise.interval
        exercise.rest = 2
        db.session.commit()

        addPoints(db, 1)




    allExercises = Exercise.query.order_by("completedLast").all()

    return render_template("exercise.html", exercises = allExercises, player = player)


@app.route('/', methods=['GET', 'POST'])
def index():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        daily.completedLast = datetime.datetime.now()
        daily.rest = daily.restDuration
        db.session.commit()

        addPoints(db, daily.totalPoints())

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

    isWork = 0 if datetime.datetime.today().weekday in (5, 6) else 1
    print(isWork)

    allDailies = Daily.query.filter(Daily.subtype != "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).all()
    stats = DailyStats(allDailies)

    openDailies = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).filter(Daily.subtype != "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).order_by(Daily.points.desc(), "availableAfter", "availableUntil").all()
    openSideQuests = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).filter(Daily.subtype == "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).order_by("rest",Daily.points.desc()).all()
    completedDailies = Daily.query.filter_by(completed=True).order_by("completedLast",Daily.availableAfter.desc()).all()
    missedDailies = Daily.query.filter_by(completed=False).filter(hour >= Daily.availableUntil).filter(Daily.subtype != "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).order_by("availableAfter", "availableUntil").all()
    #missedDailies = Daily.query.filter_by(completed=False).filter(hour > Daily.availableUntil).filter(Daily.subtype != "Side").filter(Daily.isWork == isWork or Daily.isWork == 0).order_by("availableAfter", "availableUntil").all()
    return render_template("index.html", dailies = openDailies, completed = completedDailies, missed = missedDailies, sideQuests = openSideQuests, stats = stats, player = player)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = PORT)

