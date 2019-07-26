from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable = False)

class BG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    BG = db.Column(db.Integer, unique=False, nullable = False)
    insulin = db.Column(db.Integer, unique=False, nullable = False)
    user = db.Integer, db.ForeignKey('user.id', nullable = False)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    subtype = db.Column(db.String, nullable = True)
    availableAfter = db.Column(db.Integer, nullable = False, default = 0)
    availableUntil = db.Column(db.Integer, nullable = False, default = 24)
    completed = db.Column(db.Boolean, default = False, nullable = False)
    user = db.Integer, db.ForeignKey('user.id', nullable = False)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = request.form
    if result.get("complete"):
        daily_id = result.get("daily_id")
        daily = db.session.query(Daily).get(daily_id)   
        daily.completed = True
        db.session.commit()

    if result.get("delete_daily"):
        daily_id = result.get("daily_id")
        daily = db.session.delete(Daily).where(daily_id)   
        daily.completed = True
        db.session.commit()

    if result.get("reset_dailies"):
        Daily.query.update({Daily.completed: False})
        db.session.commit()
        

    if result.get("new_daily"):
        db.session.add(Daily(name=result.get("new_daily")))
        db.session.commit()
       

    dailies = Daily.query.all()

    return render_template("index.html", dailies = dailies)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

