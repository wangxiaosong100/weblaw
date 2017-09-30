"""
The flask application package.
"""

from flask import Flask
from config import DevConfig
from weblog.MongoDB_Models import mongo

app = Flask(__name__)
app.config.from_object(DevConfig)
mongo.init_app(app)


import weblog.views
