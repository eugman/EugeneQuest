from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable = False)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    completed = db.Column(db.Boolean, nullable = False)
    user = db.Integer, db.ForeignKey('user.id', nullable = False)

@app.route('/')
def index():
    output = "<html><head></head><body><ul>"
    dailies = Daily.query.all()
    for daily in dailies:
        output += "<li>"+daily.name+"</li>"

    output +="</body></html>"

    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #db.session.add(User(username="Eugene"))
    #db.session.commit()

    #print(User.query.all())

