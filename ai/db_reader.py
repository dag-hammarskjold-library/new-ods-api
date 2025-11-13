"""
Database Reader Module for odsActions Database
Provides read-only access to the MongoDB database for querying data.
NO modifications, creations, or deletions are performed.
"""

from pymongo import MongoClient
from decouple import config
from datetime import datetime
import json
from typing import Dict, List, Optional, Any, Union

# Database connection
_DB_CLIENT = None
_DB_DATABASE = None

def get_database():
    """
    Get or create database connection.
    Uses singleton pattern to reuse connection.
    
    Returns:
        Database: MongoDB database instance
    """
    global _DB_CLIENT, _DB_DATABASE
    
    if _DB_DATABASE is None:
        try:
            conn_string = config("CONN")
            _DB_CLIENT = MongoClient(conn_string)
            _DB_DATABASE = _DB_CLIENT["odsActions"]
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    return _DB_DATABASE


def _remove_password_fields(doc: Dict) -> Dict:
    """
    Remove password fields from a document to ensure they are never displayed.
    This is a security measure to prevent password exposure.
    
    Args:
        doc: MongoDB document dictionary
        
    Returns:
        Dictionary with password fields removed
    """
    if not isinstance(doc, dict):
        return doc
    
    # Remove password field (case-insensitive check)
    keys_to_remove = []
    for key in doc.keys():
        if 'password' in key.lower():
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del doc[key]
    
    # Recursively check nested dictionaries
    for key, value in doc.items():
        if isinstance(value, dict):
            doc[key] = _remove_password_fields(value)
        elif isinstance(value, list):
            doc[key] = [_remove_password_fields(item) if isinstance(item, dict) else item for item in value]
    
    return doc


def _convert_document_for_json(doc: Dict) -> Dict:
    """
    Convert MongoDB document to JSON-serializable format.
    Converts ObjectId to string and datetime objects to ISO format strings.
    Also removes password fields for security.
    
    Args:
        doc: MongoDB document dictionary
        
    Returns:
        Dictionary with converted values and passwords removed
    """
    # First remove password fields
    doc = _remove_password_fields(doc)
    
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    # Convert all datetime fields to ISO format strings
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc


def query_users(email: Optional[str] = None, site: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Query users collection (read-only).
    
    Args:
        email: Filter by email (optional)
        site: Filter by site code (optional)
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of user documents (without passwords)
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_users_collection"]
        query = {}
        
        if email:
            query["email"] = email
        if site:
            query["site"] = site
        
        results = list(collection.find(query, {"password": 0}).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying users: {e}")
        return []


def query_sites(code_site: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Query sites collection (read-only).
    
    Args:
        code_site: Filter by site code (optional)
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of site documents
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_sites_collection"]
        query = {}
        
        if code_site:
            query["code_site"] = code_site
        
        results = list(collection.find(query).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying sites: {e}")
        return []


def query_logs_by_date_range(start_date: datetime, end_date: Optional[datetime] = None,
                             limit: int = 10000) -> List[Dict]:
    """
    Query logs within a date range, grouped by day (read-only).
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range (optional, defaults to now)
        limit: Maximum number of results (default: 10000)
        
    Returns:
        List of log documents grouped by day
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_logs_collection"]
        
        if end_date is None:
            end_date = datetime.now()
        
        query = {
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        results = list(collection.find(query).sort("date", 1).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying logs by date range: {e}")
        return []


def query_logs(user: Optional[str] = None, action: Optional[str] = None, 
               start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
               limit: int = 100) -> List[Dict]:
    """
    Query logs collection (read-only).
    
    Args:
        user: Filter by user email (optional)
        action: Filter by action description (optional)
        start_date: Filter logs from this date (optional)
        end_date: Filter logs until this date (optional)
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of log documents, sorted by date descending
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_logs_collection"]
        query = {}
        
        if user:
            query["user"] = user
        if action:
            query["action"] = {"$regex": action, "$options": "i"}  # Case-insensitive search
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        
        results = list(collection.find(query).sort("date", -1).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying logs: {e}")
        return []


def query_analytics(user: Optional[str] = None, action: Optional[str] = None,
                   start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[Dict]:
    """
    Query analytics collection (read-only).
    
    Args:
        user: Filter by user email (optional)
        action: Filter by action type (optional)
        start_date: Filter analytics from this date (optional)
        end_date: Filter analytics until this date (optional)
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of analytics documents, sorted by date descending
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        query = {}
        
        if user:
            query["user"] = user
        if action:
            query["action"] = {"$regex": action, "$options": "i"}  # Case-insensitive search
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        
        results = list(collection.find(query).sort("date", -1).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying analytics: {e}")
        return []


def query_analytics_by_date_range(start_date: datetime, end_date: Optional[datetime] = None,
                                  limit: int = 10000) -> List[Dict]:
    """
    Query analytics within a date range (read-only).
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range (optional, defaults to now)
        limit: Maximum number of results (default: 10000)
        
    Returns:
        List of analytics documents within the date range
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        if end_date is None:
            end_date = datetime.now()
        
        query = {
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        results = list(collection.find(query).sort("date", 1).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying analytics by date range: {e}")
        return []


def query_analytics_by_action_type(action_type: str, limit: int = 100) -> List[Dict]:
    """
    Query analytics by specific action type (read-only).
    Common action types: "loading_symbol_endpoint", "create_metadata_ods", "exporttoodswithfile"
    
    Args:
        action_type: Action type to filter by
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of analytics documents for the specified action type
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        query = {
            "action": {"$regex": action_type, "$options": "i"}  # Case-insensitive
        }
        
        results = list(collection.find(query).sort("date", -1).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying analytics by action type: {e}")
        return []


def get_analytics_action_types() -> List[str]:
    """
    Get list of unique action types in analytics collection (read-only).
    
    Returns:
        List of unique action type strings
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        pipeline = [
            {"$group": {"_id": "$action"}},
            {"$project": {"action": "$_id", "_id": 0}},
            {"$sort": {"action": 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        return [doc.get("action", "") for doc in results if doc.get("action")]
    except Exception as e:
        print(f"Error getting analytics action types: {e}")
        return []


def get_analytics_summary() -> Dict[str, Any]:
    """
    Get summary statistics for analytics collection (read-only).
    
    Returns:
        Dictionary with analytics summary statistics
    """
    try:
        db = get_database()
        if db is None:
            return {"error": "Database not available"}
        
        collection = db["ods_actions_analytics_collection"]
        
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_records": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user"},
                    "unique_actions": {"$addToSet": "$action"},
                    "earliest_date": {"$min": "$date"},
                    "latest_date": {"$max": "$date"}
                }
            },
            {
                "$project": {
                    "total_records": 1,
                    "unique_user_count": {"$size": "$unique_users"},
                    "unique_action_count": {"$size": "$unique_actions"},
                    "unique_actions": 1,
                    "earliest_date": 1,
                    "latest_date": 1,
                    "_id": 0
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        if results:
            summary = results[0]
            # Convert dates for JSON serialization
            _convert_document_for_json(summary)
            return summary
        else:
            return {"total_records": 0, "unique_user_count": 0, "unique_action_count": 0}
    except Exception as e:
        return {"error": f"Error getting analytics summary: {str(e)}"}


def count_files_sent_from_analytics() -> Dict[str, Any]:
    """
    Count files sent using analytics collection (read-only).
    Looks for analytics records with action related to file sending/upload.
    
    Returns:
        Dictionary with file sending statistics
    """
    try:
        db = get_database()
        if db is None:
            return {"error": "Database not available"}
        
        collection = db["ods_actions_analytics_collection"]
        
        # Look for actions related to file sending
        # Based on code: action is "send_file_endpoint" (from ods/__init__.py)
        file_actions = ["send_file_endpoint", "send_file", "exporttoodswithfile", "file_upload", "upload_file"]
        
        # Build regex pattern to match any file-related action
        action_pattern = "|".join(file_actions)
        
        pipeline = [
            {
                "$match": {
                    "action": {"$regex": action_pattern, "$options": "i"}
                }
            },
            {
                "$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "total_files": {
                        "$sum": {
                            "$cond": [
                                {"$isArray": "$data"},
                                {"$size": "$data"},
                                0
                            ]
                        }
                    },
                    "unique_users": {"$addToSet": "$user"}
                }
            },
            {
                "$project": {
                    "action": "$_id",
                    "analytics_records": "$count",
                    "estimated_files_sent": "$total_files",
                    "unique_users_count": {"$size": "$unique_users"},
                    "_id": 0
                }
            },
            {"$sort": {"analytics_records": -1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Also get total count of file-related analytics
        total_file_analytics = collection.count_documents({
            "action": {"$regex": action_pattern, "$options": "i"}
        })
        
        # Calculate total files from data arrays
        # Structure: data is a list of reports, each report is a list of file results
        total_files = 0
        file_analytics = collection.find({
            "action": {"$regex": action_pattern, "$options": "i"}
        }, {"data": 1})
        
        for doc in file_analytics:
            if "data" in doc and isinstance(doc["data"], list):
                # data is a list of reports (one per docsymbol)
                for report in doc["data"]:
                    if isinstance(report, list):
                        # report is a list of file results
                        for file_result in report:
                            if isinstance(file_result, dict):
                                result = file_result.get("result", "")
                                # Check for successful sends
                                if "downloaded and sent successfully" in str(result).lower():
                                    total_files += 1
                            elif isinstance(file_result, str):
                                if "downloaded and sent successfully" in file_result.lower():
                                    total_files += 1
                    elif isinstance(report, dict):
                        # If report is directly a dict (single file result)
                        result = report.get("result", "")
                        if "downloaded and sent successfully" in str(result).lower():
                            total_files += 1
        
        summary = {
            "total_file_analytics_records": total_file_analytics,
            "total_files_sent": total_files,
            "breakdown_by_action": results
        }
        
        # Convert dates for JSON serialization
        for item in summary.get("breakdown_by_action", []):
            _convert_document_for_json(item)
        
        return summary
    except Exception as e:
        return {"error": f"Error counting files sent: {str(e)}"}


def count_files_sent_simple() -> int:
    """
    Simple count of files sent from analytics (read-only).
    Returns just the number without detailed breakdown.
    
    Returns:
        int: Total number of files sent, or -1 if error
    """
    try:
        db = get_database()
        if db is None:
            return -1
        
        collection = db["ods_actions_analytics_collection"]
        
        # Look for file-related actions
        # Based on code: action is "send_file_endpoint" (from ods/__init__.py)
        file_actions = ["send_file_endpoint", "send_file", "exporttoodswithfile", "file_upload", "upload_file"]
        action_pattern = "|".join(file_actions)
        
        # Count files from data arrays
        # Structure: data is a list of reports, each report is a list of file results
        # Each file result has: {filename, docsymbol, language, jobnumber, result}
        total_files = 0
        file_analytics = collection.find({
            "action": {"$regex": action_pattern, "$options": "i"}
        }, {"data": 1})
        
        for doc in file_analytics:
            if "data" in doc and isinstance(doc["data"], list):
                # data is a list of reports (one per docsymbol)
                for report in doc["data"]:
                    if isinstance(report, list):
                        # report is a list of file results
                        for file_result in report:
                            if isinstance(file_result, dict):
                                result = file_result.get("result", "")
                                # Check for successful sends
                                if "downloaded and sent successfully" in str(result).lower():
                                    total_files += 1
                            elif isinstance(file_result, str):
                                if "downloaded and sent successfully" in file_result.lower():
                                    total_files += 1
                    elif isinstance(report, dict):
                        # If report is directly a dict (single file result)
                        result = report.get("result", "")
                        if "downloaded and sent successfully" in str(result).lower():
                            total_files += 1
        
        return total_files
    except Exception as e:
        print(f"Error counting files sent: {e}")
        return -1


def query_job_numbers(docsymbol: Optional[str] = None, language: Optional[str] = None,
                     jobnumber_value: Optional[str] = None, limit: int = 100, 
                     sort_by_date: bool = False) -> List[Dict]:
    """
    Query job numbers collection (read-only).
    
    Args:
        docsymbol: Filter by document symbol (optional)
        language: Filter by language code (AR, ZH, EN, FR, RU, ES, DE) (optional)
        jobnumber_value: Filter by job number value (optional)
        limit: Maximum number of results (default: 100)
        sort_by_date: If True, sort by created_date descending (most recent first)
        
    Returns:
        List of job number documents
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_jobnumbers_collection"]
        query = {}
        
        if docsymbol:
            query["docsymbol"] = docsymbol
        if language:
            query["language"] = language
        if jobnumber_value:
            query["jobnumber_value"] = jobnumber_value
        
        # Build query with optional sorting
        if sort_by_date:
            results = list(collection.find(query).sort("created_date", -1).limit(limit))
        else:
            results = list(collection.find(query).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying job numbers: {e}")
        return []


def query_ods_job_numbers(jobnumber_value: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Query ODS job number collection (read-only).
    This collection tracks released/not used job numbers.
    
    Args:
        jobnumber_value: Filter by job number value (optional)
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of ODS job number documents
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_jobnumber_collection"]
        query = {}
        
        if jobnumber_value:
            query["jobnumber_value"] = jobnumber_value
        
        results = list(collection.find(query).limit(limit))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error querying ODS job numbers: {e}")
        return []


def get_collection_stats(collection_name: str) -> Dict[str, Any]:
    """
    Get statistics about a collection (read-only).
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dictionary with collection statistics
    """
    try:
        db = get_database()
        if db is None:
            return {"error": "Database not available"}
        
        collection = db[collection_name]
        
        stats = {
            "collection_name": collection_name,
            "document_count": collection.estimated_document_count(),
            "exists": collection_name in db.list_collection_names()
        }
        
        return stats
    except Exception as e:
        return {"error": f"Error getting stats: {str(e)}"}


def get_collection_count(collection_name: str) -> int:
    """
    Get the number of records in a collection (read-only).
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        int: Number of documents in the collection, or -1 if error
    """
    try:
        db = get_database()
        if db is None:
            return -1
        
        if collection_name not in db.list_collection_names():
            return -1
        
        collection = db[collection_name]
        return collection.estimated_document_count()
    except Exception as e:
        print(f"Error getting collection count for {collection_name}: {e}")
        return -1


def get_all_collection_counts() -> Dict[str, int]:
    """
    Get the number of records in all collections (read-only).
    
    Returns:
        Dictionary mapping collection names to their record counts
    """
    try:
        db = get_database()
        if db is None:
            return {}
        
        collections = db.list_collection_names()
        counts = {}
        
        for collection_name in collections:
            try:
                collection = db[collection_name]
                count = collection.estimated_document_count()
                counts[collection_name] = count
            except Exception as e:
                print(f"Error counting {collection_name}: {e}")
                counts[collection_name] = -1
        
        return counts
    except Exception as e:
        print(f"Error getting all collection counts: {e}")
        return {}


def get_database_info() -> Dict[str, Any]:
    """
    Get information about the database structure (read-only).
    
    Returns:
        Dictionary with database information
    """
    try:
        db = get_database()
        if db is None:
            return {"error": "Database not available"}
        
        collections = db.list_collection_names()
        
        info = {
            "database_name": "odsActions",
            "collections": collections,
            "collection_count": len(collections)
        }
        
        # Get stats for each collection
        collection_stats = {}
        for coll_name in collections:
            collection_stats[coll_name] = get_collection_stats(coll_name)
        
        info["collection_stats"] = collection_stats
        
        return info
    except Exception as e:
        return {"error": f"Error getting database info: {str(e)}"}


def search_database(query_text: str, limit: int = 50) -> Dict[str, List[Dict]]:
    """
    Search across multiple collections for a query text (read-only).
    
    Args:
        query_text: Text to search for
        limit: Maximum results per collection (default: 50)
        
    Returns:
        Dictionary with results from each collection
    """
    results = {
        "users": [],
        "sites": [],
        "logs": [],
        "analytics": [],
        "job_numbers": [],
        "ods_job_numbers": []
    }
    
    try:
        # Search users by email
        if "@" in query_text:  # Looks like an email
            results["users"] = query_users(email=query_text, limit=limit)
        
        # Search sites by code or label
        results["sites"] = query_sites(code_site=query_text.upper()[:3], limit=limit)
        
        # Search logs by action or user
        results["logs"] = query_logs(action=query_text, limit=limit)
        
        # Search analytics by action or user
        results["analytics"] = query_analytics(action=query_text, limit=limit)
        
        # Search job numbers by docsymbol or jobnumber
        results["job_numbers"] = query_job_numbers(
            docsymbol=query_text if "/" in query_text else None,
            jobnumber_value=query_text if query_text.startswith(("NX", "NY", "GE", "VI")) else None,
            limit=limit
        )
        
        # Search ODS job numbers
        results["ods_job_numbers"] = query_ods_job_numbers(
            jobnumber_value=query_text if query_text.startswith(("NX", "NY", "GE", "VI")) else None,
            limit=limit
        )
        
    except Exception as e:
        print(f"Error in search_database: {e}")
    
    return results


def group_users_by_site(limit: int = 100) -> List[Dict]:
    """
    Group users by site (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with site and user count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_users_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$site",
                "count": {"$sum": 1},
                "users": {"$push": {"email": "$email", "show_display": "$show_display", 
                                   "show_create_update": "$show_create_update", 
                                   "show_send_file": "$show_send_file",
                                   "show_jobnumbers_management": "$show_jobnumbers_management",
                                   "show_parameters": "$show_parameters"}}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "site": "$_id",
                "user_count": "$count",
                "users": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization and remove passwords
        for doc in results:
            _convert_document_for_json(doc)
            if "users" in doc:
                for user in doc["users"]:
                    _convert_document_for_json(user)
        
        return results
    except Exception as e:
        print(f"Error grouping users by site: {e}")
        return []


def group_logs_by_user(limit: int = 100) -> List[Dict]:
    """
    Group logs by user (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with user and log count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_logs_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$user",
                "count": {"$sum": 1},
                "latest_log": {"$max": "$date"},
                "earliest_log": {"$min": "$date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "user": "$_id",
                "log_count": "$count",
                "latest_log": 1,
                "earliest_log": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping logs by user: {e}")
        return []


def group_logs_by_action(limit: int = 100) -> List[Dict]:
    """
    Group logs by action type (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with action and log count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_logs_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$action",
                "count": {"$sum": 1},
                "latest_log": {"$max": "$date"},
                "earliest_log": {"$min": "$date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "action": "$_id",
                "log_count": "$count",
                "latest_log": 1,
                "earliest_log": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping logs by action: {e}")
        return []


def group_job_numbers_by_language(limit: int = 100) -> List[Dict]:
    """
    Group job numbers by language (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with language and job number count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_jobnumbers_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$language",
                "count": {"$sum": 1},
                "latest_jobnumber": {"$max": "$created_date"},
                "earliest_jobnumber": {"$min": "$created_date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "language": "$_id",
                "jobnumber_count": "$count",
                "latest_jobnumber": 1,
                "earliest_jobnumber": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping job numbers by language: {e}")
        return []


def group_job_numbers_by_docsymbol(limit: int = 100) -> List[Dict]:
    """
    Group job numbers by document symbol (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with docsymbol and job number count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_jobnumbers_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$docsymbol",
                "count": {"$sum": 1},
                "languages": {"$addToSet": "$language"},
                "latest_jobnumber": {"$max": "$created_date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "docsymbol": "$_id",
                "jobnumber_count": "$count",
                "languages": 1,
                "latest_jobnumber": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping job numbers by docsymbol: {e}")
        return []


def group_analytics_by_action(limit: int = 100) -> List[Dict]:
    """
    Group analytics by action type (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with action and analytics count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$action",
                "count": {"$sum": 1},
                "latest_analytics": {"$max": "$date"},
                "earliest_analytics": {"$min": "$date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "action": "$_id",
                "analytics_count": "$count",
                "latest_analytics": 1,
                "earliest_analytics": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping analytics by action: {e}")
        return []


def group_analytics_by_user(limit: int = 100) -> List[Dict]:
    """
    Group analytics by user (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with user and analytics count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        pipeline = [
            {"$group": {
                "_id": "$user",
                "count": {"$sum": 1},
                "latest_analytics": {"$max": "$date"},
                "earliest_analytics": {"$min": "$date"},
                "actions": {"$addToSet": "$action"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "user": "$_id",
                "analytics_count": "$count",
                "action_types": {"$size": "$actions"},
                "unique_actions": "$actions",
                "latest_analytics": 1,
                "earliest_analytics": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping analytics by user: {e}")
        return []


def group_analytics_by_day(start_date: datetime, end_date: Optional[datetime] = None,
                          limit: int = 1000) -> List[Dict]:
    """
    Group analytics by day within a date range (read-only aggregation).
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range (optional, defaults to now)
        limit: Maximum number of groups (default: 1000)
        
    Returns:
        List of grouped results with date and analytics count per day
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        if end_date is None:
            end_date = datetime.now()
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    },
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user"},
                    "unique_actions": {"$addToSet": "$action"},
                    "analytics": {
                        "$push": {
                            "user": "$user",
                            "action": "$action",
                            "date": "$date"
                        }
                    }
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": limit},
            {"$project": {
                "date": "$_id",
                "analytics_count": "$count",
                "unique_users_count": {"$size": "$unique_users"},
                "unique_actions_count": {"$size": "$unique_actions"},
                "unique_actions": "$unique_actions",
                "analytics": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
            if "analytics" in doc:
                for analytics_item in doc["analytics"]:
                    _convert_document_for_json(analytics_item)
        
        return results
    except Exception as e:
        print(f"Error grouping analytics by day: {e}")
        return []


def group_analytics_by_action_and_user(limit: int = 100) -> List[Dict]:
    """
    Group analytics by both action type and user (read-only aggregation).
    
    Args:
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results with action, user, and count
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_analytics_collection"]
        
        pipeline = [
            {"$group": {
                "_id": {
                    "action": "$action",
                    "user": "$user"
                },
                "count": {"$sum": 1},
                "latest_date": {"$max": "$date"},
                "earliest_date": {"$min": "$date"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "action": "$_id.action",
                "user": "$_id.user",
                "analytics_count": "$count",
                "latest_date": 1,
                "earliest_date": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error grouping analytics by action and user: {e}")
        return []


def get_collection_summary(collection_name: str) -> Dict[str, Any]:
    """
    Get summary statistics for a collection (read-only aggregation).
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        db = get_database()
        if db is None:
            return {"error": "Database not available"}
        
        if collection_name not in db.list_collection_names():
            return {"error": f"Collection '{collection_name}' not found"}
        
        collection = db[collection_name]
        
        # Get total count
        total_count = collection.estimated_document_count()
        
        # Get field statistics if possible
        pipeline = [
            {"$project": {"_id": 0}},
            {"$limit": 1000}  # Sample for field analysis
        ]
        
        sample_docs = list(collection.aggregate(pipeline))
        
        summary = {
            "collection_name": collection_name,
            "total_documents": total_count,
            "sampled_documents": len(sample_docs)
        }
        
        # Analyze fields if we have documents
        if sample_docs:
            field_types = {}
            for doc in sample_docs:
                for key, value in doc.items():
                    if key not in field_types:
                        field_types[key] = set()
                    field_types[key].add(type(value).__name__)
            
            summary["fields"] = {k: list(v) for k, v in field_types.items()}
        
        return summary
    except Exception as e:
        return {"error": f"Error getting collection summary: {str(e)}"}


def group_logs_by_day(start_date: datetime, end_date: Optional[datetime] = None,
                     limit: int = 1000) -> List[Dict]:
    """
    Group logs by day within a date range (read-only aggregation).
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range (optional, defaults to now)
        limit: Maximum number of groups (default: 1000)
        
    Returns:
        List of grouped results with date and log count per day
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        collection = db["ods_actions_logs_collection"]
        
        if end_date is None:
            end_date = datetime.now()
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    },
                    "count": {"$sum": 1},
                    "logs": {
                        "$push": {
                            "user": "$user",
                            "action": "$action",
                            "date": "$date"
                        }
                    }
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": limit},
            {"$project": {
                "date": "$_id",
                "log_count": "$count",
                "logs": 1,
                "_id": 0
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
            if "logs" in doc:
                for log in doc["logs"]:
                    _convert_document_for_json(log)
        
        return results
    except Exception as e:
        print(f"Error grouping logs by day: {e}")
        return []


def execute_group_query(collection_name: str, group_by_field: str, 
                       additional_fields: Optional[List[str]] = None,
                       limit: int = 100) -> List[Dict]:
    """
    Execute a generic group query on any collection (read-only).
    
    Args:
        collection_name: Name of the collection
        group_by_field: Field to group by
        additional_fields: Additional fields to include in results (optional)
        limit: Maximum number of groups (default: 100)
        
    Returns:
        List of grouped results
    """
    try:
        db = get_database()
        if db is None:
            return []
        
        if collection_name not in db.list_collection_names():
            return []
        
        collection = db[collection_name]
        
        # Build projection for additional fields
        project_fields = {
            "group_value": f"${group_by_field}",
            "count": {"$sum": 1},
            "_id": 0
        }
        
        if additional_fields:
            for field in additional_fields:
                project_fields[field] = f"${field}"
        
        pipeline = [
            {"$group": {
                "_id": f"${group_by_field}",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": project_fields}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert documents for JSON serialization
        for doc in results:
            _convert_document_for_json(doc)
        
        return results
    except Exception as e:
        print(f"Error executing group query: {e}")
        return []

