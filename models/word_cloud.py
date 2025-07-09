from utils.db import db

class WordCloud(db.Model):
    __tablename__ = 'data_word_cloud'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    word = db.Column(db.String(25))
    count = db.Column(db.Integer)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))