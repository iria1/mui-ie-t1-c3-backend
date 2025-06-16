from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WordCloud(db.Model):
    __tablename__ = 'data_word_cloud'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    word = db.Column(db.String(25))
    count = db.Column(db.Integer)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))

class BullyStatRegional(db.Model):
    __tablename__ = 'data_bully_stat_regional'

    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))
    total_pct = db.Column(db.Integer)
    male_pct = db.Column(db.Integer)
    female_pct = db.Column(db.Integer)
    source = db.Column(db.String(100))
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))