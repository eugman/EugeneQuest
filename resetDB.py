import app
import os

os.remove("test.db")
app.db.create_all()

