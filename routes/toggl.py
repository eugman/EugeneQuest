from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy


@app.route('/toggl', methods=['GET', 'POST'])
def toggle():
    result = request.form
    player = db.session.query(Player).get(1)
 
    toggl_client = TogglClientApi(toggleSettings)
    
    workspaces = toggl_client.get_workspaces()

    print(workspaces)
    return render_template("toggl.html", player = player)


