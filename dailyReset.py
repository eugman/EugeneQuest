from app import *
from app.models import Player, Daily, NegThoughtsLog
player = db.session.query(Player).get(1)

ntl = NegThoughtsLog(thoughts = player.negThoughts)


db.session.add(ntl)

player.prevNegThoughts = player.negThoughts
player.negThoughts = 0
player.prevPointsGained = player.pointsGained
player.pointsGained = 0
Daily.query.update({Daily.completed: False})
db.session.commit()
