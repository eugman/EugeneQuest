from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable = False)


@app.route('/')
def index():
    return "Hello world test!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #db.session.add(User(username="Eugene"))
    #db.session.commit()

    #print(User.query.all())

