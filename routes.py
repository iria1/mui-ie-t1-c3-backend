import logging
from flask import request, jsonify
from app import app, db
from utils import validate_request_params, format_error_response, sanitize_string
from models import *
from sqlalchemy import func

logger = logging.getLogger(__name__)

@app.route('/api/')
def index():
    """API root endpoint with basic information"""
    return jsonify({
        "name": "ChildCyberCare API",
        "version": "1.0.0",
        "description": "REST API for C3 App",
        "endpoints": {
            "GET /": "List endpoints",
            "GET /get_word_cloud": "Get word cloud data"
        }
    })

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
    bullystat = BullyStatRegional.query.filter_by(active=1).all()

    data = [ bs.region for bs in bullystat ] 

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

# @app.route('/api/users')
# def get_user():
#     users = User.query.all()
    
#     users_data = [
#         {
#             "id": user.id,
#             "name": user.name
#         } for user in users
#     ]

#     return jsonify({
#         "data": users_data
#     }), 200
    
# @app.route('/api/user')
# def get_user_with_get():
#     user_id = request.args.get('id')

#     user = User.query.get(user_id)

#     return jsonify({
#         "id": user.id,
#         "name": user.name
#     }), 200

# @app.route('/api/user', methods=['POST'])
# def get_user_with_post():
#     data = request.get_json()

#     user_id = data['id']
#     user = User.query.get(user_id)

#     return jsonify({
#         "id": user.id,
#         "name": user.name
#     }), 200

# @app.route('/api/post')
# def get_post_of_user():
#     user_id = request.args.get('user_id')

#     posts = Post.query.filter_by(user_id=user_id)

#     data_posts = [
#         {
#             "title": post.title,
#             "author": post.author.name
#         } for post in posts
#     ]

#     return jsonify({
#         "data": data_posts
#     }), 200

# @app.route('/api/get_word_cloud_dummy')
# def get_word_cloud_dummy():
#     data = [
#         ['JavaScript', 50],
#         ['HTML', 30],
#         ['CSS', 20],
#         ['React', 25],
#         ['Web', 15],
#         ['Cloud', 10],
#         ['Visualization', 18],
#         ['GitHub', 22]
#     ]

#     return jsonify({
#         "data": data
#     }), 200