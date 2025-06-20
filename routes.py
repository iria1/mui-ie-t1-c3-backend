import logging
from flask import request, jsonify
from app import app
from utils import format_error_response
from models import *
from sqlalchemy import func

logger = logging.getLogger(__name__)

@app.route('/api/')
def index():
    # health check
    return jsonify({
        "status": "OK"
    }), 200

@app.route('/api/get_word_cloud')
def get_word_cloud():
    arg_ver = request.args.get('ver')
    arg_count = request.args.get('count')

    max_version = WordCloud.query.with_entities(func.max(WordCloud.version)).scalar()

    # check if dataset argument version is valid
    # if unspecified, use default (highest version)
    if arg_ver is None:
        ver = max_version
    else:
        # test if arg is int
        # if not, fallback
        try:
            ver = int(arg_ver)
        except ValueError:
            ver = max_version
        
        # if version number is invalid, fallback
        if ver < 1 or ver > max_version:
            ver = max_version
    
    # show 30 (default) top words for the wordcloud
    # can be adjusted to between 1 to 50
    if arg_count is None:
        count = 30
    else:
        try:
            count = int(arg_count)
        except ValueError:
            count = 30
        
        if count < 1 or count > 50:
            count = 30

    # query DB
    wordcloud = WordCloud.query.filter_by(
        active=1,
        version=ver
        ).order_by(WordCloud.count.desc()).limit(count).all()

    # normalize count for compatibility with frontend
    MIN_SIZE = 10
    MAX_SIZE = 50

    counts = [wc.count for wc in wordcloud]
    min_count = min(counts)
    max_count = max(counts)

    for wc in wordcloud:
        normalized = (wc.count - min_count) / (max_count - min_count)
        wc.count = int(MIN_SIZE + normalized * (MAX_SIZE - MIN_SIZE))

    # prepare data format
    data = [
        [
            wc.word,
            wc.count
        ] for wc in wordcloud
    ]

    return jsonify({
        "data": data
    }), 200

@app.route('/api/get_bully_stat')
def get_bully_stat():
    # query db
    bullystat = BullyStatRegional.query.filter_by(active=1, region="ASEAN").all()

    # if data is missing, replace with total_pct
    for bs in bullystat:
        if bs.female_pct is None:
            bs.female_pct = bs.total_pct
        if bs.male_pct is None:
            bs.male_pct = bs.total_pct

    # prepare data format
    data = [
        {
            "country": bs.country,
            "region": bs.region,
            "total_pct": bs.total_pct,
            "male_pct": bs.male_pct,
            "female_pct": bs.female_pct,
            "source": bs.source
        } for bs in bullystat
    ]

    return jsonify({
        "data": data
    }), 200

@app.route('/api/get_bully_stat_region_list')
def get_bully_stat_region_list():
    # query db
    bullystat = BullyStatRegional.query.filter_by(active=1, region="ASEAN").all()

    # prepare data format
    # chart.js requires code & name format for multi-select combo box
    data = [
        {
            "code": bs.country,
            "name": bs.country
        } for bs in bullystat
    ]

    return jsonify({
        "data": data
    }), 200

@app.route('/api/get_socmed_usage')
def get_socmed_usage():
    # query db
    socmed = SocmedMental.query.all()

    # prepare data format
    # chart.js requires x,y,c for colored scatterplots
    data = [
        {
            "x": float(sm.daily_socmed_usage_hrs),
            "y": float(sm.daily_sleep_hrs),
            "c": sm.mental_health_score
        } for sm in socmed
    ]

    return jsonify({
        "data": data
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify(format_error_response("The requested endpoint does not exist")), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify(format_error_response("Method not allowed for this endpoint")), 405

@app.errorhandler(500)
def server_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify(format_error_response("Internal server error")), 500