from utils.db import db

class BullyStatRegional(db.Model):
    __tablename__ = 'data_bully_stat_regional'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    total_pct = db.Column(db.Integer)
    male_pct = db.Column(db.Integer)
    female_pct = db.Column(db.Integer)
    source = db.Column(db.String(100))
    region = db.Column(db.String(100))
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))