
from flask import Flask
from config import DevConfig
from weblog.MongoDB_Models import mongo

#from flask_msearch import Search
#from jieba.analyse import ChineseAnalyzer

#analyzer=ChineseAnalyzer()
#search=Search()
app = Flask(__name__)

app.config.from_object(DevConfig)
#app.config.setdefault('MSEARCH_BACKEND', 'whoosh')
mongo.init_app(app)
#search.init_app(app,mongo,analyzer)
import weblog.views


