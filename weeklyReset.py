from app import db
from app.models import *

Weekly.query.update({Daily.completed: False})
db.session.commit()
