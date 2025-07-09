from db import db

class SocmedMental(db.Model):
    __tablename__ = 'data_socmed_mental'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    acad_level = db.Column(db.String(25))
    country = db.Column(db.String(50))
    daily_socmed_usage_hrs = db.Column(db.Numeric(10,2))
    daily_sleep_hrs = db.Column(db.Numeric(10,2))
    mental_health_score = db.Column(db.Integer)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=str('1'))