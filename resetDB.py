import app
import os

if os.path.exists("test.db"): 
    os.remove("test.db")
app.db.create_all()

app.db.session.add(app.User(username="Eugene"))
app.db.session.add(app.Daily(name="Check Blood Sugar", user = 1))
app.db.session.commit()

