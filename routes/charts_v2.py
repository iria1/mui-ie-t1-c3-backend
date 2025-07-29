from flask import Blueprint, request, jsonify
from models import WordCloudV2, BullyStatRegional, SocmedMental
from utils.jwt import require_token

charts_v2_bp = Blueprint('charts_v2_bp', __name__, url_prefix='/v2/charts')

@charts_v2_bp.route('/get_word_cloud')
@require_token
def get_word_cloud():
    arg_label = request.args.get('label')
    arg_count = request.args.get('count')

    # check if dataset argument version is valid
    # if unspecified, use default (highest version)
    if arg_label is None:
        label = "Not Cool"
    else:
        if arg_label == "nc":
            label = "Not Cool"
        elif arg_label == "ng":
            label = "No Go"
        else:
            label = "Not Cool"
    
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
    wordcloud = WordCloudV2.query.filter_by(
        active=1,
        label=label
        ).order_by(WordCloudV2.frequency.desc()).limit(count).all()

    # normalize count for compatibility with frontend
    MIN_SIZE = 10
    MAX_SIZE = 50

    counts = [wc.frequency for wc in wordcloud]
    min_count = min(counts)
    max_count = max(counts)

    for wc in wordcloud:
        normalized = (wc.frequency - min_count) / (max_count - min_count)
        wc.frequency = int(MIN_SIZE + normalized * (MAX_SIZE - MIN_SIZE))

    # prepare data format
    data = [
        [
            wc.word,
            wc.frequency
        ] for wc in wordcloud
    ]

    return jsonify({
        "data": data
    }), 200

@charts_v2_bp.route('/get_bully_stat')
@require_token
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

@charts_v2_bp.route('/get_bully_stat_region_list')
@require_token
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

@charts_v2_bp.route('/get_socmed_usage')
@require_token
def get_socmed_usage():
    # query db
    socmed = SocmedMental.query.all()

    # prepare data format
    # chart.js requires x,y,c for colored scatterplots
    data = [
        {
            "x_socmed": float(sm.daily_socmed_usage_hrs),
            "x_sleep": float(sm.daily_sleep_hrs),
            "y": sm.mental_health_score
        } for sm in socmed
    ]

    return jsonify({
        "data": data
    }), 200