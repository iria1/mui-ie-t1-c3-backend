from utils.db import db

class WordCloudV2(db.Model):
    __tablename__ = 'data_word_cloud_v2'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(25))
    frequency = db.Column(db.Integer)
    label = db.Column(db.String(25))
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))