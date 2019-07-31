from app import *
player = db.session.query(Player).get(1)
ntl = NegThoughtsLog(thoughts = player.negThoughts)

db.session.add(ntl)


player.negThoughts = 0
Daily.query.update({Daily.completed: False})
db.session.commit()
