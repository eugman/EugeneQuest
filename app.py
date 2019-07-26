import datetime
from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False)

class BG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    BG = db.Column(db.Integer,  nullable = False)
    insulin = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.Integer, db.ForeignKey('user.id', nullable = False, default = 1)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    subtype = db.Column(db.String, nullable = True)
    availableAfter = db.Column(db.Integer, nullable = False, default = 0)
    availableUntil = db.Column(db.Integer, nullable = False, default = 24)
    completed = db.Column(db.Boolean, default = False, nullable = False)
    user = db.Integer, db.ForeignKey('user.id', nullable = False, default = 1)

    def json(self):
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    reps = db.Column(db.Integer, default = 1)
    sets = db.Column(db.Integer, default = 1)
    weight = db.Column(db.Integer, default = 0)
    vest = db.Column(db.Boolean, default = False)

    def json(self):
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

class DailyStats():
        def __init__(self, dailies):
            hour = datetime.datetime.now().hour
            
            self.questCount = len(dailies)
            self.completedCount = len(list(filter(lambda x: (x.completed == True), dailies)))
            self.missedCount =  len(list(filter(lambda x: (x.completed == False and x.availableUntil < hour), dailies)))

            self.completedPercent = str(int(100.0 * self.completedCount / self.questCount))
            self.missedPercent = str(int(100.0 * self.missedCount / self.questCount))

            



@app.route('/api/openquests')
def openquests():
    output = "["
    hour = datetime.datetime.now().hour
    openDailies = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).order_by("availableAfter", "availableUntil").all()


    for daily in openDailies:
        output += daily.json() + ',\n'

    output = output[:-2] + "]"

    return Response(output, mimetype='application/json')

@app.route('/api/complete', methods=['GET', 'POST'])
def complete():
    result = request.form
    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        db.session.commit()
        if result.get("bg"):
            db.session.add(BG(BG=result.get("bg"), insulin=result.get("insulin")))
            db.session.commit()





@app.route('/add', methods=['GET', 'POST'])
def add():
    result = request.form

    if result.get("new_daily"):
        db.session.add(Daily(name=result.get("new_daily")))
        db.session.commit()

    return render_template("add.html")


@app.route('/exercise', methods=['GET', 'POST'])
def index():
    result = request.form
    if result.get("update"):
        daily_id = result.get("exercise_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        db.session.commit()


    allExercises = Exercise.query.all()

    return render_template("exercise.html", exercises = allExercises)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = request.form
    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        db.session.commit()

        if result.get("bg"):
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

    openDailies = Daily.query.filter_by(completed=False).filter(Daily.availableAfter <= hour).filter(Daily.availableUntil > hour).order_by("availableAfter", "availableUntil").all()
    completedDailies = Daily.query.filter_by(completed=True).order_by("availableAfter", "availableUntil").all()
    missedDailies = Daily.query.filter_by(completed=False).filter(Daily.availableUntil < hour).order_by("availableAfter", "availableUntil").all()

    return render_template("index.html", dailies = openDailies, completed = completedDailies, missed = missedDailies, stats = stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

