import sys, os
INTERP = "/home/eugman/opt/python-3.6.2/bin/python3"
#INTERP is present twice so that the new Python interpreter knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
from app import app as application
