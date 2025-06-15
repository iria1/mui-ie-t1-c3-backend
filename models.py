from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WordCloud(db.Model):
    __tablename__ = 'data_word_cloud'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(25))
    count = db.Column(db.Integer)
    active = db.Column(db.Boolean)