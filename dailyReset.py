from app import *
from app.models import Player, Daily
player = db.session.query(Player).get(1)
player.negThoughts = 0
Daily.query.update({Daily.completed: False})
db.session.commit()
