from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, timezone
from flask_pymongo import PyMongo
from bson import json_util
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/ods"
mongo = PyMongo(app)

@app.route('/')
def index():
    logger.debug("Index route accessed")
    return render_template('base.html')

@app.route('/get_analytics')
def get_analytics():
    try:
        time_range = request.args.get('timeRange', 'week')
        
        # Calculate start date based on time range
        end_date = datetime.now(timezone.utc)
        if time_range == 'today':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'week':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        elif time_range == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)  # Default to week
        
        # Get analytics collection
        analytics_collection = mongo.db.ods_actions_analytics_collection
        
        # Get total actions
        total_actions = analytics_collection.count_documents({
            'date': {'$gte': start_date, '$lte': end_date}
        })
        
        # Get unique users
        unique_users = len(analytics_collection.distinct('user', {
            'date': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Get most active user
        pipeline = [
            {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {'_id': '$user', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ]
        most_active = list(analytics_collection.aggregate(pipeline))
        most_active_user = most_active[0]['_id'] if most_active else 'No activity'
        
        # Get recent activity
        recent_activity = list(analytics_collection.find(
            {'date': {'$gte': start_date, '$lte': end_date}},
            {'_id': 1, 'date': 1, 'user': 1, 'action': 1, 'details': 1}
        ).sort('date', -1).limit(10))
        
        # Get action types distribution
        action_types = {}
        pipeline = [
            {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {'_id': '$action', 'count': {'$sum': 1}}}
        ]
        for result in analytics_collection.aggregate(pipeline):
            action_types[result['_id']] = result['count']
        
        # Get time series data
        pipeline = [
            {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$date'},
                    'month': {'$month': '$date'},
                    'day': {'$dayOfMonth': '$date'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}}
        ]
        time_series = []
        for result in analytics_collection.aggregate(pipeline):
            date = datetime(result['_id']['year'], result['_id']['month'], result['_id']['day'])
            time_series.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': result['count']
            })
        
        # Get user tasks distribution
        user_tasks = {}
        pipeline = [
            {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {'_id': '$user', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        for result in analytics_collection.aggregate(pipeline):
            user_tasks[result['_id']] = result['count']
        
        return jsonify({
            'totalActions': total_actions,
            'uniqueUsers': unique_users,
            'mostActiveUser': most_active_user,
            'recentActivity': recent_activity,
            'actionTypes': action_types,
            'timeSeriesData': time_series,
            'userTasks': user_tasks
        })
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/check_collection')
def check_collection():
    try:
        # Check if collection exists
        collection = mongo.db.ods_actions_analytics_collection
        count = collection.count_documents({})
        
        # Get a sample document
        sample = collection.find_one()
        
        return jsonify({
            'status': 'success',
            'collection_exists': True,
            'document_count': count,
            'sample_document': json.loads(json_util.dumps(sample)) if sample else None
        })
    except Exception as e:
        logger.error(f"Error in check_collection: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 