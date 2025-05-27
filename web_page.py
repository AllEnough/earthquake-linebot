# 負責地震資料網頁顯示
from flask import Blueprint, render_template
from pymongo import MongoClient

web_page = Blueprint('web_page', __name__)

# MongoDB 連線
client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['earthquake_db']
collection = db['earthquakes']

@web_page.route('/')
def index():
    quakes = collection.find().sort('origin_time', -1).limit(10)
    return render_template('index.html', quakes=quakes)
