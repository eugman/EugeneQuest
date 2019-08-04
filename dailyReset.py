from app import db
from app.models import *
player = db.session.query(Player).get(1)

ntl = NegThoughtsLog(thoughts = player.negThoughts)


db.session.add(ntl)

player.prevNegThoughts = player.negThoughts
player.negThoughts = 0
player.prevPointsGained = player.pointsGained
player.pointsGained = 0

Daily.query.update({Daily.completed: False})

db.session.query(Exercise).update({Exercise.rest: Exercise.rest - 1})
db.session.query(Daily).update({Daily.rest: Daily.rest - 1})

db.session.commit()
