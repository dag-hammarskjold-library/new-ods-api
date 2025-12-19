"""
Chatbot module using Hugging Face Llama-3.1-8B-Instruct for ODS Actions Help
This module provides a chatbot interface that uses the extracted PDF documentation
to answer user questions about the ODS Actions application.
"""

import os
import sys
import re
import json
import requests
import urllib.parse
from pathlib import Path
from decouple import config

# Import database reader for querying odsActions database
try:
    from . import db_reader
    DB_READER_AVAILABLE = True
except ImportError:
    try:
        import db_reader
        DB_READER_AVAILABLE = True
    except ImportError:
        DB_READER_AVAILABLE = False

# Hugging Face API configuration
HF_API_AVAILABLE = True
# List of models to try in order (will try each until one works)
# Using models that are more likely to work - trying basic text generation models
# These are publicly available and don't require special access
# NOTE: If all models fail, consider using OpenAI API or a local model
HF_MODELS_TO_TRY = [
    "gpt2",                      # Very accessible, basic text generation
    "distilgpt2",                # Smaller GPT-2 variant, very accessible
    "google/flan-t5-small",      # Small instruction-following model
    "google/flan-t5-base",       # Base model, instruction following
]
# Start with the first model
HF_MODEL = HF_MODELS_TO_TRY[0]
# Use the router API endpoint for inference (inference API is deprecated)
HF_API_URL = f"https://router.huggingface.co/models/{HF_MODEL}"

# Load documentation from extracted text file (already extracted)
_DOCUMENTATION_CACHE = ""

def load_documentation_from_file():
    """
    Load ODS_ACTIONS_DOCUMENTATION from the already extracted text file.
    This loads the documentation from extracted_documentation.txt (not from PDF).
    The model uses this text documentation to answer questions - no PDF extraction needed.
    This is faster and more reliable than extracting from PDF each time.
    """
    global _DOCUMENTATION_CACHE
    
    if _DOCUMENTATION_CACHE:
        return _DOCUMENTATION_CACHE
    
    try:
        # Get the directory where this script is located
        ai_dir = Path(__file__).parent
        
        # Try to load from extracted text file
        extracted_file = ai_dir / "extracted_documentation.txt"
        
        if extracted_file.exists():
            with open(extracted_file, 'r', encoding='utf-8') as f:
                _DOCUMENTATION_CACHE = f.read()
                return _DOCUMENTATION_CACHE
        
        # Fallback: Try to import from pdf_extractor if file doesn't exist
        try:
            from pdf_extractor import DOCUMENTATION_TEXT
            if DOCUMENTATION_TEXT:
                _DOCUMENTATION_CACHE = DOCUMENTATION_TEXT
                return _DOCUMENTATION_CACHE
        except ImportError:
            # If running from parent directory, add ai folder to path
            if str(ai_dir) not in sys.path:
                sys.path.insert(0, str(ai_dir))
            from pdf_extractor import DOCUMENTATION_TEXT
            if DOCUMENTATION_TEXT:
                _DOCUMENTATION_CACHE = DOCUMENTATION_TEXT
                return _DOCUMENTATION_CACHE
        
        return ""
        
    except Exception as e:
        print(f"Warning: Could not load documentation: {e}", file=sys.stderr)
        return ""

# Load documentation once at module import
_DOCUMENTATION_CACHE = load_documentation_from_file()


def initialize_hf():
    """
    Initialize Hugging Face API with API key from environment variables.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    if not HF_API_AVAILABLE:
        return False
    
    try:
        # Get API key from environment variable
        api_key = config("HF_API_KEY", default=None)
        
        # Try alternative names if HF_API_KEY not found
        if not api_key:
            api_key = config("HUGGINGFACE_API_KEY", default=None)
        if not api_key:
            api_key = config("HUGGING_FACE_API_KEY", default=None)
        if not api_key:
            # Try from os.environ directly as fallback
            import os
            api_key = os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HUGGING_FACE_API_KEY")
        
        if not api_key:
            print("Error: HF_API_KEY not found in environment variables")
            print("Please add HF_API_KEY=your_key_here to your .env file")
            return False
        
        # Test API key by making a simple request (skip test for router API, just verify key exists)
        # Router API might not support GET requests, so we'll test during actual inference
        return True
        
        if test_response.status_code == 200 or test_response.status_code == 503:  # 503 means model is loading
            return True
        else:
            print(f"Error: Hugging Face API returned status {test_response.status_code}")
            return False
    except Exception as e:
        print(f"Error initializing Hugging Face API: {e}")
        return False


# Cache the API key to avoid re-reading it
_HF_API_KEY = None

def get_hf_api_key():
    """
    Get the Hugging Face API key from environment variables.
    
    Returns:
        str or None: The API key, or None if unavailable
    """
    global _HF_API_KEY
    
    if _HF_API_KEY is not None:
        return _HF_API_KEY
    
    try:
        # Try to get the API key from environment
        api_key = config("HF_API_KEY", default=None)
        
        # If not found, try alternative names
        if not api_key:
            api_key = config("HUGGINGFACE_API_KEY", default=None)
        if not api_key:
            api_key = config("HUGGING_FACE_API_KEY", default=None)
        if not api_key:
            # Try from os.environ directly as fallback
            import os
            api_key = os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HUGGING_FACE_API_KEY")
        
        if api_key:
            _HF_API_KEY = api_key
            return api_key
        else:
            print("Error: HF_API_KEY not found in environment variables.")
            print("Please add HF_API_KEY=your_key_here to your .env file")
            return None
            except Exception as e:
        print(f"Error getting HF_API_KEY: {e}")
        return None


def get_chatbot_model():
    """
    Get the Hugging Face model configuration for chat.
    This function is kept for compatibility but returns True if API is available.
    
    Returns:
        bool: True if API is available, False otherwise
    """
    if not HF_API_AVAILABLE:
        return None
                
    api_key = get_hf_api_key()
    if not api_key:
        return None
    
    return True  # Return True to indicate API is available


# Cache the system prompt to avoid recreating it every time
_SYSTEM_PROMPT_CACHE = None

def detect_database_query(user_message: str) -> bool:
    """
    Detect if the user's message is asking about database information.
    
    Args:
        user_message: The user's message
        
    Returns:
        bool: True if the message seems to be about database queries
    """
    db_keywords = [
        "database", "db", "collection", "user", "users", "site", "sites",
        "log", "logs", "analytics", "job number", "job numbers", "jobnumber",
        "how many", "count", "list", "show", "find", "search", "query",
        "what data", "what information", "retrieve", "get data",
        "group", "grouped", "grouping", "by", "aggregate", "aggregation",
        "summary", "statistics", "stats", "number of records", "number of documents",
        "record count", "document count", "total records", "total documents"
    ]
    
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in db_keywords)


def get_database_context(user_message: str) -> str:
    """
    Query the database based on the user's message and return formatted results.
    This function performs READ-ONLY operations.
    
    Args:
        user_message: The user's message
        
    Returns:
        str: Formatted database query results or empty string
    """
    if not DB_READER_AVAILABLE:
        return ""
    
    try:
        message_lower = user_message.lower()
        results_parts = []
        
        # Check for specific queries
        if "user" in message_lower or "users" in message_lower:
            if "@" in user_message:
                # Extract email if present
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_message)
                if emails:
                    users = db_reader.query_users(email=emails[0], limit=10)
                    if users:
                        results_parts.append(f"Users found: {json.dumps(users, indent=2)}")
            else:
                users = db_reader.query_users(limit=20)
                if users:
                    results_parts.append(f"Users (showing first 20): {json.dumps(users, indent=2)}")
        
        if "site" in message_lower or "sites" in message_lower:
            sites = db_reader.query_sites(limit=50)
            if sites:
                results_parts.append(f"Sites: {json.dumps(sites, indent=2)}")
        
        if "log" in message_lower and "analytics" not in message_lower:
            # Check for date range queries (e.g., "since november first", "since nov 1", "from november 1")
            from datetime import datetime, timedelta
            
            # Try to extract date information
            date_patterns = [
                r"since\s+(november|nov|dec|december|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october)\s+(\d+)",
                r"from\s+(november|nov|dec|december|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october)\s+(\d+)",
                r"since\s+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
                r"from\s+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})"
            ]
            
            start_date = None
            for pattern in date_patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    try:
                        if "november" in match.group(0).lower() or "nov" in match.group(0).lower():
                            day = int(match.group(2)) if match.lastindex >= 2 else 1
                            current_year = datetime.now().year
                            start_date = datetime(current_year, 11, day)
                        elif "since" in message_lower or "from" in message_lower:
                            # Try to parse other dates
                            day = int(match.group(2)) if match.lastindex >= 2 else 1
                            current_year = datetime.now().year
                            start_date = datetime(current_year, 11, day)
                        break
                    except:
                        pass
            
            # Check for "per day" or "by day" grouping
            if "per day" in message_lower or "by day" in message_lower or "each day" in message_lower:
                if start_date:
                    grouped = db_reader.group_logs_by_day(start_date, limit=365)
                    if grouped:
                        results_parts.append(f"Logs grouped by day since {start_date.strftime('%Y-%m-%d')}: {json.dumps(grouped, indent=2)}")
                else:
                    # Default to November 1st if not specified
                    current_year = datetime.now().year
                    start_date = datetime(current_year, 11, 1)
                    grouped = db_reader.group_logs_by_day(start_date, limit=365)
                    if grouped:
                        results_parts.append(f"Logs grouped by day since November 1st: {json.dumps(grouped, indent=2)}")
            elif start_date:
                logs = db_reader.query_logs_by_date_range(start_date, limit=1000)
                if logs:
                    results_parts.append(f"Logs since {start_date.strftime('%Y-%m-%d')} (showing first 1000): {json.dumps(logs, indent=2)}")
            else:
                logs = db_reader.query_logs(limit=50)
                if logs:
                    results_parts.append(f"Recent logs (showing first 50): {json.dumps(logs, indent=2)}")
        
        if "analytics" in message_lower:
            # Check for date range queries
            from datetime import datetime
            
            start_date = None
            date_patterns = [
                r"since\s+(november|nov|dec|december|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october)\s+(\d+)",
                r"from\s+(november|nov|dec|december|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october)\s+(\d+)",
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    try:
                        if "november" in match.group(0).lower() or "nov" in match.group(0).lower():
                            day = int(match.group(2)) if match.lastindex >= 2 else 1
                            current_year = datetime.now().year
                            start_date = datetime(current_year, 11, day)
                            break
                    except:
                        pass
            
            # Check for specific queries - files sent
            if "file" in message_lower and ("sent" in message_lower or "send" in message_lower or "upload" in message_lower):
                # For "how many" queries, use simple count to avoid truncation
                if "how many" in message_lower or "count" in message_lower or "number" in message_lower:
                    file_count = db_reader.count_files_sent_simple()
                    if file_count >= 0:
                        results_parts.append(f"Total files sent: {file_count}")
                    else:
                        # Fallback to detailed stats if simple count fails
                        file_stats = db_reader.count_files_sent_from_analytics()
                        if file_stats and "error" not in file_stats:
                            total = file_stats.get("total_files_sent", 0)
                            results_parts.append(f"Total files sent: {total}")
                else:
                    # For detailed queries, return full statistics
                    file_stats = db_reader.count_files_sent_from_analytics()
                    if file_stats and "error" not in file_stats:
                        results_parts.append(f"Files sent statistics: {json.dumps(file_stats, indent=2)}")
            elif "summary" in message_lower or "statistics" in message_lower or "stats" in message_lower:
                summary = db_reader.get_analytics_summary()
                if summary:
                    results_parts.append(f"Analytics summary: {json.dumps(summary, indent=2)}")
            elif "action types" in message_lower or "action type" in message_lower or "types of actions" in message_lower:
                action_types = db_reader.get_analytics_action_types()
                if action_types:
                    results_parts.append(f"Analytics action types: {json.dumps(action_types, indent=2)}")
            elif "per day" in message_lower or "by day" in message_lower or "each day" in message_lower:
                if start_date:
                    grouped = db_reader.group_analytics_by_day(start_date, limit=365)
                    if grouped:
                        results_parts.append(f"Analytics grouped by day since {start_date.strftime('%Y-%m-%d')}: {json.dumps(grouped, indent=2)}")
                else:
                    # Default to November 1st if not specified
                    current_year = datetime.now().year
                    start_date = datetime(current_year, 11, 1)
                    grouped = db_reader.group_analytics_by_day(start_date, limit=365)
                    if grouped:
                        results_parts.append(f"Analytics grouped by day since November 1st: {json.dumps(grouped, indent=2)}")
            elif "by action" in message_lower and "by user" in message_lower:
                grouped = db_reader.group_analytics_by_action_and_user(limit=100)
                if grouped:
                    results_parts.append(f"Analytics grouped by action and user: {json.dumps(grouped, indent=2)}")
            elif start_date:
                analytics = db_reader.query_analytics_by_date_range(start_date, limit=1000)
                if analytics:
                    results_parts.append(f"Analytics since {start_date.strftime('%Y-%m-%d')} (showing first 1000): {json.dumps(analytics, indent=2)}")
            else:
                # Default: return basic analytics or count
                if "how many" in message_lower or "count" in message_lower or "number" in message_lower:
                    # For count queries, just return the count
                    count = db_reader.get_collection_count("ods_actions_analytics_collection")
                    if count >= 0:
                        results_parts.append(f"Total analytics records: {count}")
                else:
                    # For general queries, return recent analytics
                    analytics = db_reader.query_analytics(limit=50)
                    if analytics:
                        results_parts.append(f"Analytics (showing first 50): {json.dumps(analytics, indent=2)}")
                    else:
                        # Fallback: at least return the count
                        count = db_reader.get_collection_count("ods_actions_analytics_collection")
                        if count >= 0:
                            results_parts.append(f"Total analytics records: {count}")
        
        if "job number" in message_lower or "jobnumber" in message_lower:
            # Check if asking for total/count first (before other queries)
            if "total" in message_lower or ("how many" in message_lower and "job" in message_lower):
                count = db_reader.get_collection_count("ods_actions_jobnumbers_collection")
                if count >= 0:
                    results_parts.append(f"Total job numbers: {count}")
                else:
                    # Fallback: try to get count from query
                    job_nums = db_reader.query_job_numbers(limit=1000)
                    if job_nums:
                        results_parts.append(f"Total job numbers (estimated, showing up to 1000): {len(job_nums)}")
            # Check for "last" or "recent" queries
            elif "last" in message_lower or "recent" in message_lower or "created" in message_lower:
                # Extract number if specified (e.g., "last 100", "last 50")
                limit = 100  # default
                limit_match = re.search(r'last\s+(\d+)|recent\s+(\d+)|(\d+)\s+created', message_lower)
                if limit_match:
                    for group in limit_match.groups():
                        if group:
                            limit = int(group)
                            break
                
                # Query job numbers sorted by created_date descending
                job_nums = db_reader.query_job_numbers(limit=limit, sort_by_date=True)
                if job_nums:
                    results_parts.append(f"Last {len(job_nums)} job numbers created: {json.dumps(job_nums, indent=2)}")
                else:
                    # Fallback to regular query
                    job_nums = db_reader.query_job_numbers(limit=limit)
                    if job_nums:
                        results_parts.append(f"Job numbers (showing first {len(job_nums)}): {json.dumps(job_nums, indent=2)}")
            else:
                # Try to extract docsymbol or jobnumber from message
                # Look for document symbols (e.g., A/RES/68/123)
                docsymbols = re.findall(r'[A-Z]/[A-Z]+/\d+/\d+', user_message)
                # Look for job numbers (e.g., NX900000)
                jobnumbers = re.findall(r'[A-Z]{2}\d+', user_message)
                
                if docsymbols:
                    job_nums = db_reader.query_job_numbers(docsymbol=docsymbols[0], limit=20)
                    if job_nums:
                        results_parts.append(f"Job numbers for {docsymbols[0]}: {json.dumps(job_nums, indent=2)}")
                elif jobnumbers:
                    job_nums = db_reader.query_job_numbers(jobnumber_value=jobnumbers[0], limit=20)
                    if job_nums:
                        results_parts.append(f"Job number {jobnumbers[0]}: {json.dumps(job_nums, indent=2)}")
                else:
                    job_nums = db_reader.query_job_numbers(limit=50)
                    if job_nums:
                        results_parts.append(f"Job numbers (showing first 50): {json.dumps(job_nums, indent=2)}")
        
        if "database info" in message_lower or "database structure" in message_lower or "collections" in message_lower:
            db_info = db_reader.get_database_info()
            if db_info:
                results_parts.append(f"Database information: {json.dumps(db_info, indent=2)}")
        
        if "how many" in message_lower or "count" in message_lower or "number of records" in message_lower or "number of documents" in message_lower:
            # Check if asking for all collections
            if "all collection" in message_lower or "each collection" in message_lower or "every collection" in message_lower:
                all_counts = db_reader.get_all_collection_counts()
                if all_counts:
                    counts_formatted = json.dumps(all_counts, indent=2)
                    results_parts.append(f"Record counts for all collections:\n{counts_formatted}")
            
            # Try to determine what to count
            elif "user" in message_lower:
                count = db_reader.get_collection_count("ods_actions_users_collection")
                if count >= 0:
                    results_parts.append(f"Total users: {count}")
                else:
                    users = db_reader.query_users(limit=1000)
                    results_parts.append(f"Total users (estimated): {len(users)}")
            elif "site" in message_lower:
                count = db_reader.get_collection_count("ods_actions_sites_collection")
                if count >= 0:
                    results_parts.append(f"Total sites: {count}")
                else:
                    sites = db_reader.query_sites(limit=1000)
                    results_parts.append(f"Total sites (estimated): {len(sites)}")
            elif "log" in message_lower and "analytics" not in message_lower:
                count = db_reader.get_collection_count("ods_actions_logs_collection")
                if count >= 0:
                    results_parts.append(f"Total logs: {count}")
                else:
                    logs = db_reader.query_logs(limit=1000)
                    results_parts.append(f"Total logs (estimated, showing up to 1000): {len(logs)}")
            elif "analytics" in message_lower:
                count = db_reader.get_collection_count("ods_actions_analytics_collection")
                if count >= 0:
                    results_parts.append(f"Total analytics records: {count}")
                else:
                    # Fallback: try to get count from query
                    analytics = db_reader.query_analytics(limit=1000)
                    if analytics:
                        results_parts.append(f"Total analytics (estimated, showing up to 1000): {len(analytics)}")
                    else:
                        results_parts.append(f"Total analytics records: 0")
            elif "job number" in message_lower or "jobnumber" in message_lower:
                count = db_reader.get_collection_count("ods_actions_jobnumbers_collection")
                if count >= 0:
                    results_parts.append(f"Total job numbers: {count}")
                else:
                    job_nums = db_reader.query_job_numbers(limit=1000)
                    results_parts.append(f"Total job numbers (estimated, showing up to 1000): {len(job_nums)}")
            else:
                # If no specific collection mentioned, show all counts
                all_counts = db_reader.get_all_collection_counts()
                if all_counts:
                    counts_formatted = json.dumps(all_counts, indent=2)
                    results_parts.append(f"Record counts for all collections:\n{counts_formatted}")
        
        # Ensure analytics queries are always handled
        if "analytics" in message_lower and not any("analytics" in part.lower() for part in results_parts):
            # If analytics was mentioned but no results yet, provide basic info
            if "how many" in message_lower or "count" in message_lower or "number" in message_lower:
                count = db_reader.get_collection_count("ods_actions_analytics_collection")
                if count >= 0:
                    results_parts.append(f"Total analytics records: {count}")
            else:
                # Provide summary for general analytics queries
                summary = db_reader.get_analytics_summary()
                if summary and "error" not in summary:
                    results_parts.append(f"Analytics summary: {json.dumps(summary, indent=2)}")
                else:
                    count = db_reader.get_collection_count("ods_actions_analytics_collection")
                    if count >= 0:
                        results_parts.append(f"Total analytics records: {count}")
        
        # Handle group queries
        if "group" in message_lower or "grouped" in message_lower or "grouping" in message_lower:
            # Group users by site
            if "user" in message_lower and "site" in message_lower:
                grouped = db_reader.group_users_by_site(limit=50)
                if grouped:
                    results_parts.append(f"Users grouped by site: {json.dumps(grouped, indent=2)}")
            
            # Group logs by user
            elif "log" in message_lower and "user" in message_lower:
                grouped = db_reader.group_logs_by_user(limit=50)
                if grouped:
                    results_parts.append(f"Logs grouped by user: {json.dumps(grouped, indent=2)}")
            
            # Group logs by action
            elif "log" in message_lower and "action" in message_lower:
                grouped = db_reader.group_logs_by_action(limit=50)
                if grouped:
                    results_parts.append(f"Logs grouped by action: {json.dumps(grouped, indent=2)}")
            
            # Group job numbers by language
            elif ("job number" in message_lower or "jobnumber" in message_lower) and "language" in message_lower:
                grouped = db_reader.group_job_numbers_by_language(limit=50)
                if grouped:
                    results_parts.append(f"Job numbers grouped by language: {json.dumps(grouped, indent=2)}")
            
            # Group job numbers by docsymbol
            elif ("job number" in message_lower or "jobnumber" in message_lower) and ("docsymbol" in message_lower or "document symbol" in message_lower):
                grouped = db_reader.group_job_numbers_by_docsymbol(limit=50)
                if grouped:
                    results_parts.append(f"Job numbers grouped by document symbol: {json.dumps(grouped, indent=2)}")
            
            # Group analytics by action
            elif "analytics" in message_lower and "action" in message_lower:
                grouped = db_reader.group_analytics_by_action(limit=50)
                if grouped:
                    results_parts.append(f"Analytics grouped by action: {json.dumps(grouped, indent=2)}")
            
            # Group analytics by user
            elif "analytics" in message_lower and "user" in message_lower:
                grouped = db_reader.group_analytics_by_user(limit=50)
                if grouped:
                    results_parts.append(f"Analytics grouped by user: {json.dumps(grouped, indent=2)}")
            # Group analytics by day
            elif "analytics" in message_lower and ("per day" in message_lower or "by day" in message_lower):
                from datetime import datetime
                current_year = datetime.now().year
                start_date = datetime(current_year, 11, 1)
                grouped = db_reader.group_analytics_by_day(start_date, limit=365)
                if grouped:
                    results_parts.append(f"Analytics grouped by day: {json.dumps(grouped, indent=2)}")
            # Group analytics by action and user
            elif "analytics" in message_lower and "action" in message_lower and "user" in message_lower:
                grouped = db_reader.group_analytics_by_action_and_user(limit=50)
                if grouped:
                    results_parts.append(f"Analytics grouped by action and user: {json.dumps(grouped, indent=2)}")
        
        # Handle "by" queries (e.g., "users by site", "logs by user")
        if " by " in message_lower:
            parts = message_lower.split(" by ")
            if len(parts) == 2:
                entity = parts[0].strip()
                group_field = parts[1].strip()
                
                if "user" in entity and "site" in group_field:
                    grouped = db_reader.group_users_by_site(limit=50)
                    if grouped:
                        results_parts.append(f"Users grouped by site: {json.dumps(grouped, indent=2)}")
                elif "log" in entity and "user" in group_field:
                    grouped = db_reader.group_logs_by_user(limit=50)
                    if grouped:
                        results_parts.append(f"Logs grouped by user: {json.dumps(grouped, indent=2)}")
                elif "log" in entity and "action" in group_field:
                    grouped = db_reader.group_logs_by_action(limit=50)
                    if grouped:
                        results_parts.append(f"Logs grouped by action: {json.dumps(grouped, indent=2)}")
                elif ("job number" in entity or "jobnumber" in entity) and "language" in group_field:
                    grouped = db_reader.group_job_numbers_by_language(limit=50)
                    if grouped:
                        results_parts.append(f"Job numbers grouped by language: {json.dumps(grouped, indent=2)}")
                elif "analytics" in entity and "action" in group_field:
                    grouped = db_reader.group_analytics_by_action(limit=50)
                    if grouped:
                        results_parts.append(f"Analytics grouped by action: {json.dumps(grouped, indent=2)}")
                elif "analytics" in entity and "user" in group_field:
                    grouped = db_reader.group_analytics_by_user(limit=50)
                    if grouped:
                        results_parts.append(f"Analytics grouped by user: {json.dumps(grouped, indent=2)}")
                elif "analytics" in entity and "day" in group_field:
                    from datetime import datetime
                    current_year = datetime.now().year
                    start_date = datetime(current_year, 11, 1)
                    grouped = db_reader.group_analytics_by_day(start_date, limit=365)
                    if grouped:
                        results_parts.append(f"Analytics grouped by day: {json.dumps(grouped, indent=2)}")
        
        # Handle summary/statistics queries
        if "summary" in message_lower or "statistics" in message_lower or "stats" in message_lower:
            if "collection" in message_lower:
                # Try to extract collection name
                for coll_name in ["users", "sites", "logs", "analytics", "job numbers", "jobnumbers"]:
                    if coll_name in message_lower:
                        if coll_name == "users":
                            summary = db_reader.get_collection_summary("ods_actions_users_collection")
                        elif coll_name == "sites":
                            summary = db_reader.get_collection_summary("ods_actions_sites_collection")
                        elif coll_name == "logs":
                            summary = db_reader.get_collection_summary("ods_actions_logs_collection")
                        elif coll_name == "analytics":
                            summary = db_reader.get_collection_summary("ods_actions_analytics_collection")
                        elif coll_name in ["job numbers", "jobnumbers"]:
                            summary = db_reader.get_collection_summary("ods_actions_jobnumbers_collection")
                        
                        if summary:
                            results_parts.append(f"Collection summary: {json.dumps(summary, indent=2)}")
                        break
        
        # If no specific query matched, do a general search
        if not results_parts:
            # Check if it's a general analytics question first
            if "analytics" in message_lower:
                # Try to get analytics count or summary
                if "how many" in message_lower or "count" in message_lower or "number" in message_lower:
                    count = db_reader.get_collection_count("ods_actions_analytics_collection")
                    if count >= 0:
                        results_parts.append(f"Total analytics records: {count}")
                    else:
                        # Fallback: try query
                        analytics = db_reader.query_analytics(limit=1000)
                        if analytics:
                            results_parts.append(f"Total analytics records (estimated): {len(analytics)}")
                else:
                    # Return summary for general analytics queries
                    summary = db_reader.get_analytics_summary()
                    if summary and "error" not in summary:
                        results_parts.append(f"Analytics summary: {json.dumps(summary, indent=2)}")
                    else:
                        # Fallback to count
                        count = db_reader.get_collection_count("ods_actions_analytics_collection")
                        if count >= 0:
                            results_parts.append(f"Total analytics records: {count}")
                        else:
                            # Last resort: return recent analytics
                            analytics = db_reader.query_analytics(limit=20)
                            if analytics:
                                results_parts.append(f"Recent analytics (showing first 20): {json.dumps(analytics, indent=2)}")
            
            # General database search (only if still no results)
            if not results_parts:
                search_results = db_reader.search_database(user_message, limit=10)
                for collection, data in search_results.items():
                    if data:
                        results_parts.append(f"{collection}: {json.dumps(data, indent=2)}")
        
        if results_parts:
            return "\n\n=== DATABASE QUERY RESULTS ===\n" + "\n\n".join(results_parts) + "\n\n=== END DATABASE RESULTS ===\n"
        
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return f"\n\nNote: Database query encountered an error: {str(e)}\n"
    
    return ""


def create_system_prompt():
    """
    Create the system prompt with documentation context.
    Uses cached prompt for better performance.
    
    Returns:
        str: System prompt with documentation
    """
    global _SYSTEM_PROMPT_CACHE
    
    # Return cached prompt if available
    if _SYSTEM_PROMPT_CACHE:
        return _SYSTEM_PROMPT_CACHE
    
    # Use cached documentation instead of extracting each time
    documentation = _DOCUMENTATION_CACHE if _DOCUMENTATION_CACHE else "Documentation not available"
    
    # Add database query capabilities to the prompt
    db_capabilities = ""
    if DB_READER_AVAILABLE:
        db_capabilities = """

DATABASE QUERY CAPABILITIES:
You can answer questions about the odsActions MongoDB database. The database contains:
- Users collection (ods_actions_users_collection): User accounts with permissions
- Sites collection (ods_actions_sites_collection): Site configurations
- Logs collection (ods_actions_logs_collection): System activity logs
- Analytics collection (ods_actions_analytics_collection): Detailed analytics data
- Job Numbers collection (ods_actions_jobnumbers_collection): Job number tracking
- ODS Job Number collection (ods_jobnumber_collection): Released job numbers

When users ask about database information, you will receive query results that you can use to answer their questions.

GROUP QUERY CAPABILITIES:
You can answer group/aggregation queries such as:
- "Group users by site" - Shows users organized by their site
- "Logs grouped by user" - Shows log counts per user
- "Logs grouped by action" - Shows log counts per action type
- "Job numbers by language" - Shows job number counts per language
- "Job numbers by document symbol" - Shows job numbers grouped by docsymbol
- "Analytics by action" - Shows analytics counts per action type
- "Analytics by user" - Shows analytics counts per user
- "Summary of [collection]" - Shows collection statistics

IMPORTANT: You can only READ from the database. No modifications, creations, or deletions are allowed. All group queries are read-only aggregations.

SECURITY CONSTRAINT - CRITICAL:
NEVER display, reveal, or mention passwords in any form. Passwords are automatically filtered from all database queries and should NEVER appear in your responses. If a user asks about passwords, explain that passwords are securely hashed and stored, but never display any password values, even if they appear in query results."""
    
    # Create optimized, concise prompt
    prompt = f"""You are a helpful assistant for ODS Actions - an Official Document System management tool.

Use this documentation to answer questions:

{documentation}
{db_capabilities}

Guidelines:
- Answer questions about ODS Actions features and usage
- Answer questions about database data when provided in query results
- Provide step-by-step instructions when needed
- Be concise and accurate
- Reference documentation sections when relevant
- When presenting database results, format them clearly and summarize key information
- If unrelated to ODS Actions, redirect politely

CRITICAL SECURITY RULE:
- NEVER display, reveal, or mention passwords in any form
- Passwords are automatically filtered from all database queries
- If asked about passwords, explain they are securely hashed and stored, but never show password values
- If you see any password field in query results, ignore it completely

Be helpful, friendly, and professional."""
    
    # Cache the prompt
    _SYSTEM_PROMPT_CACHE = prompt
    return prompt


def chat_with_gemini(user_message, conversation_history=None):
    """
    Send a message to Hugging Face Llama model and get a response.
    This function is kept for backward compatibility but now uses Hugging Face.
    
    Args:
        user_message (str): The user's question/message
        conversation_history (list, optional): Previous conversation messages (not fully supported yet)
        
    Returns:
        dict: Response dictionary with:
            - 'success' (bool): Whether the request was successful
            - 'response' (str): The bot's response text
            - 'error' (str): Error message if failed
    """
    # For now, use simple_chat which works well with Hugging Face
    # Conversation history can be added later if needed
    return simple_chat(user_message)


def simple_chat(user_message):
    """
    Simple chat function that includes documentation context in each request.
    Useful for stateless interactions.
    
    Args:
        user_message (str): The user's question
        
    Returns:
        dict: Response dictionary
    """
    if not HF_API_AVAILABLE:
        return {
            'success': False,
            'response': '',
            'error': "Hugging Face API not available. Please ensure requests library is installed."
        }
    
    # Ensure documentation is loaded
    global _DOCUMENTATION_CACHE
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        return {
            'success': False,
            'response': '',
            'error': "Documentation not loaded. Please ensure extracted_documentation.txt exists in the ai folder."
        }
    
    try:
        api_key = get_hf_api_key()
        if not api_key:
            return {
                'success': False,
                'response': '',
                'error': "Failed to get Hugging Face API key. Check HF_API_KEY in .env file."
            }
        
        # Create prompt with documentation (cached)
        system_prompt = create_system_prompt()
        
        # Check if this is a database query and get results
        db_context = ""
        if DB_READER_AVAILABLE and detect_database_query(user_message):
            db_context = get_database_context(user_message)
        
        # Format prompt for instruction-following models (FLAN-T5, Mistral, Llama, etc.)
        # Combine system prompt and user message into a single text prompt
        # FLAN-T5 models work well with this format
        full_prompt = f"""{system_prompt}

Question: {user_message}
{db_context}

Answer:"""
        
        # Prepare the payload for Hugging Face API
        # For text generation models, we pass the prompt as a string
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 1024,
                "return_full_text": False
            }
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Try models in order until one works
        response = None
        last_error = None
        used_model = None
        
        for model_name in HF_MODELS_TO_TRY:
            # Try router API first
            model_url = f"https://router.huggingface.co/models/{model_name}"
            used_model = model_name
            
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=60)
                
                # If model is loading (503), wait and retry
                if response.status_code == 503:
                    import time
                    time.sleep(5)
                    response = requests.post(model_url, headers=headers, json=payload, timeout=60)
                
                # If successful, break out of loop
                if response.status_code == 200:
                    break
                
                # If 404, try inference API as fallback (even though deprecated)
                if response.status_code == 404:
                    last_error = f"Model {model_name} not found on Router API (404)"
                    # Try inference API as fallback
                    inference_url = f"https://api-inference.huggingface.co/models/{model_name}"
                    try:
                        inference_response = requests.post(inference_url, headers=headers, json=payload, timeout=60)
                        if inference_response.status_code == 200:
                            response = inference_response
                            break
                        elif inference_response.status_code == 503:
                            import time
                            time.sleep(5)
                            inference_response = requests.post(inference_url, headers=headers, json=payload, timeout=60)
                            if inference_response.status_code == 200:
                                response = inference_response
                                break
                    except:
                        pass  # Continue to next model
                    continue
                
                # For other errors, break and report
                break
                
            except requests.exceptions.RequestException as e:
                last_error = f"Request error with {model_name}: {str(e)}"
                response = None  # Ensure response is None on exception
                continue
            except Exception as e:
                last_error = f"Unexpected error with {model_name}: {str(e)}"
                response = None  # Ensure response is None on exception
                continue
        
        # If no model worked, return error
        if not response or response.status_code != 200:
            error_msg = f"Hugging Face API error: {response.status_code if response else 'No response'}"
            try:
                if response:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error']}"
                    elif isinstance(error_data, str):
                        error_msg += f" - {error_data}"
                    elif isinstance(error_data, dict):
                        error_msg += f" - {str(error_data)}"
            except:
                if response:
                    error_text = response.text[:500] if hasattr(response, 'text') else str(response)[:500]
                    error_msg += f" - {error_text}"
            
            # If 404, provide helpful message about model access
            if not response or response.status_code == 404:
                error_msg += f"\n\nTried models: {', '.join(HF_MODELS_TO_TRY)}\n"
                error_msg += f"Last attempted: {used_model if used_model else HF_MODEL}\n"
                if used_model:
                    error_msg += f"Endpoint: https://router.huggingface.co/models/{used_model}\n\n"
                error_msg += "All models returned 404. Possible issues:\n"
                error_msg += "1. Models may require accepting terms on Hugging Face\n"
                error_msg += "2. Your API key may not have access to these models\n"
                error_msg += "3. Models may not be available through the Router API\n"
                error_msg += "4. Check Hugging Face model pages and accept terms if needed\n"
                if last_error:
                    error_msg += f"\nLast error: {last_error}"
            
                return {
                    'success': False,
                    'response': '',
                'error': error_msg
            }
        
        # Parse response
        response_data = response.json()
        
        # Hugging Face API returns a list of generated text
        if isinstance(response_data, list) and len(response_data) > 0:
            if 'generated_text' in response_data[0]:
                response_text = response_data[0]['generated_text']
            elif isinstance(response_data[0], dict) and 'text' in response_data[0]:
                response_text = response_data[0]['text']
            else:
                # Try to extract text from the response
                response_text = str(response_data[0])
        elif isinstance(response_data, dict):
            if 'generated_text' in response_data:
                response_text = response_data['generated_text']
            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")


            elif 'text' in response_data:
                response_text = response_data['text']
            else:
                response_text = str(response_data)
        else:
            response_text = str(response_data)
        
        # Clean up the response text (remove any prompt artifacts)
        if response_text:
            # Remove the original prompt if it was included
            if user_message in response_text:
                response_text = response_text.split(user_message)[-1].strip()
            if "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            return {
                'success': True,
                'response': response_text,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'error': "No response generated from Hugging Face API."
            }
        
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'error': f"Error: {str(e)}"
        }


# Alias for backward compatibility
def initialize_gemini():
    """Alias for initialize_hf() for backward compatibility"""
    return initialize_hf()

def chat_with_gemini(user_message, conversation_history=None):
    """Alias for simple_chat() for backward compatibility"""
    return simple_chat(user_message)

if __name__ == "__main__":
    # Test the chatbot
    print("Testing ODS Actions Chatbot...")
    print("=" * 60)
    
    # Check if Hugging Face API is available
    if not HF_API_AVAILABLE:
        print("✗ Hugging Face API not available")
        print("Please ensure requests library is installed: pip install requests")
        sys.exit(1)
    
    # Check documentation (no global needed at module level)
    if not _DOCUMENTATION_CACHE:
        _DOCUMENTATION_CACHE = load_documentation_from_file()
        
    if not _DOCUMENTATION_CACHE:
        print("✗ Documentation not loaded")
        print("Please ensure extracted_documentation.txt exists in the ai folder")
        sys.exit(1)
    
    print(f"✓ Documentation loaded: {len(_DOCUMENTATION_CACHE)} characters")
    
    # Test initialization
    if initialize_hf():
        print("✓ Hugging Face API initialized successfully")
        
        # Test a simple question
        print("\nTesting with sample question...")
        test_question = "How do I display metadata for a document symbol?"
        
        result = simple_chat(test_question)
        
        if result['success']:
            print(f"\nQuestion: {test_question}")
            print(f"\nAnswer:\n{result['response']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("✗ Failed to initialize Hugging Face API")
        print("Make sure HF_API_KEY is set in your .env file")

