# Database Queries Guide for ODS Actions Chatbot

This guide explains how to query the odsActions MongoDB database using the chatbot. All queries are **READ-ONLY** - no modifications, creations, or deletions are performed.

## Table of Contents

1. [Basic Collection Queries](#basic-collection-queries)
2. [Count Queries](#count-queries)
3. [Collection-Specific Queries](#collection-specific-queries)
4. [Group/Aggregation Queries](#groupaggregation-queries)
5. [Date Range Queries](#date-range-queries)
6. [Analytics Queries](#analytics-queries)
7. [Job Numbers Queries](#job-numbers-queries)
8. [Examples](#examples)

---

## Basic Collection Queries

### Get All Collection Counts

Ask for the total number of records in all collections:

- "How many records in each collection?"
- "Number of records in all collections"
- "Count of all collections"
- "Show me record counts for all collections"

### Get Count for Specific Collection

Ask for the count of a specific collection:

- "How many users?"
- "Number of sites"
- "Count of logs"
- "How many analytics records?"
- "Total job numbers"

---

## Count Queries

### General Count Queries

The chatbot understands various ways to ask for counts:

- "How many [collection]?"
- "Count of [collection]"
- "Number of [collection] records"
- "Total [collection]"
- "What's the count of [collection]?"

**Examples:**
- "How many users are in the database?"
- "What's the total number of sites?"
- "Count the logs collection"

---

## Collection-Specific Queries

### Users Collection

Query users by email or site:

- "Show me all users"
- "List users"
- "Find user with email [email@example.com]"
- "Users from site [SITE]"

**What you'll get:**
- User email
- Site assignment
- Permissions (show_display, show_create_update, etc.)
- Creation date

### Sites Collection

Query sites:

- "Show me all sites"
- "List sites"
- "What sites are available?"

**What you'll get:**
- Site code (3-letter)
- Site label/name
- Prefix for job numbers
- Creation date

### Logs Collection

Query system activity logs:

- "Show me recent logs"
- "List logs"
- "What are the recent activities?"

**What you'll get:**
- User who performed the action
- Action description
- Date/timestamp

### Analytics Collection

Query detailed analytics data:

- "Show me analytics"
- "List analytics"
- "Recent analytics data"

**What you'll get:**
- User email
- Action type
- Date/timestamp
- Detailed operation results (data array)

### Job Numbers Collection

Query job numbers:

- "Show me job numbers"
- "List job numbers"
- "Find job numbers for document symbol [A/RES/68/123]"
- "Job numbers for [NX900000]"
- "Last 100 job numbers created"
- "Recent 50 job numbers"
- "Show me the last job numbers created"
- "Total job numbers"
- "How many job numbers?"

**What you'll get:**
- Job number value
- Associated document symbol
- Language code
- Creation date

**Notes:**
- When asking for "total job numbers" or "how many job numbers", you'll get the actual count of all job numbers in the database (not just a limited sample)
- When asking for "last" or "recent" job numbers, you can specify a number (e.g., "last 100") or use the default of 100. Results are sorted by creation date with the most recent first

---

## Group/Aggregation Queries

### Group Users by Site

- "Group users by site"
- "Users grouped by site"
- "Show me users organized by site"

**What you'll get:**
- Site name
- Number of users per site
- List of users in each site

### Group Logs by User

- "Logs grouped by user"
- "Group logs by user"
- "Show me logs per user"

**What you'll get:**
- User email
- Number of logs per user
- Latest and earliest log dates

### Group Logs by Action

- "Logs grouped by action"
- "Group logs by action type"
- "Show me logs by action"

**What you'll get:**
- Action type
- Count of logs per action
- Latest and earliest log dates

### Group Job Numbers by Language

- "Job numbers by language"
- "Group job numbers by language"
- "Job numbers grouped by language"

**What you'll get:**
- Language code (AR, ZH, EN, FR, RU, ES, DE)
- Count of job numbers per language
- Date ranges

### Group Job Numbers by Document Symbol

- "Job numbers by document symbol"
- "Group job numbers by docsymbol"
- "Job numbers grouped by document symbol"

**What you'll get:**
- Document symbol
- Count of job numbers per symbol
- Languages associated with each symbol

### Group Analytics by Action

- "Analytics grouped by action"
- "Group analytics by action type"
- "Analytics by action"

**What you'll get:**
- Action type
- Count of analytics records per action
- Date ranges

### Group Analytics by User

- "Analytics grouped by user"
- "Group analytics by user"
- "Analytics by user"

**What you'll get:**
- User email
- Count of analytics records per user
- Unique action types per user
- Date ranges

### Group Analytics by Action and User

- "Analytics by action and user"
- "Group analytics by action and user"
- "Analytics grouped by action and user"

**What you'll get:**
- Action type and user combination
- Count for each combination
- Date ranges

---

## Date Range Queries

### Logs by Date Range

Query logs within a specific date range:

- "Logs since November 1st"
- "Logs from November 1"
- "Show me logs since Nov 1"

### Logs Per Day

Group logs by day within a date range:

- "Logs per day since November first"
- "Logs by day since November 1st"
- "Logs each day from November 1"

**What you'll get:**
- Date (YYYY-MM-DD)
- Number of logs per day
- List of logs for each day

### Analytics by Date Range

Query analytics within a date range:

- "Analytics since November 1st"
- "Analytics from November 1"
- "Show me analytics since Nov 1"

### Analytics Per Day

Group analytics by day:

- "Analytics per day since November first"
- "Analytics by day since November 1st"
- "Analytics each day from November 1"

**What you'll get:**
- Date (YYYY-MM-DD)
- Number of analytics records per day
- Unique users and actions per day
- List of analytics for each day

---

## Analytics Queries

### Analytics Summary

Get overall statistics about the analytics collection:

- "Analytics summary"
- "Analytics statistics"
- "Analytics stats"
- "Summary of analytics collection"

**What you'll get:**
- Total records
- Unique user count
- Unique action count
- List of all action types
- Earliest and latest dates

### Analytics Action Types

Get list of all action types:

- "Analytics action types"
- "What action types are in analytics?"
- "List analytics action types"
- "Types of actions in analytics"

**What you'll get:**
- List of all unique action types (e.g., "send_file_endpoint", "loading_symbol_endpoint", "create_metadata_ods")

### Files Sent Count

Count files that have been sent using the analytics collection:

- "How many files have been sent?"
- "Count files sent using analytics"
- "Number of files sent"
- "How many files have been sent using the analytics collection"

**What you'll get:**
- Total number of files successfully sent
- Breakdown by action type (if detailed query)

**Note:** This query looks for analytics records with action "send_file_endpoint" and counts successful file sends from the data array.

---

## Job Numbers Queries

### Query by Document Symbol

- "Job numbers for A/RES/68/123"
- "Find job numbers for document symbol [SYMBOL]"
- "Show job numbers for [SYMBOL]"

### Query by Job Number

- "Find job number NX900000"
- "Job number NX900000"
- "Show me job number [JOB_NUMBER]"

### Query by Language

- "Job numbers for language EN"
- "Job numbers in French (FR)"
- "Show job numbers for language [LANGUAGE]"

### Query Total Count

Get the total number of job numbers in the database:

- "Total job numbers"
- "How many job numbers?"
- "Count of job numbers"

**What you'll get:**
- The actual total count of all job numbers in the database
- This is the complete count, not a limited sample

**Note:** This query returns the exact count from the database, not just the first 50 or 100 results.

### Query Last/Recent Job Numbers

Query the most recently created job numbers:

- "Last 100 job numbers created"
- "Recent 50 job numbers"
- "Show me the last job numbers created"
- "Can I see the last 100 job numbers created?"

**What you'll get:**
- List of job numbers sorted by creation date (most recent first)
- Job number value, document symbol, language, and creation date
- Default limit is 100 if not specified

**Examples:**
- "Last 100 job numbers created" → Returns 100 most recent
- "Recent 50 job numbers" → Returns 50 most recent
- "Last job numbers" → Returns 100 most recent (default)

**Supported languages:** AR, ZH, EN, FR, RU, ES, DE

---

## Database Information Queries

### Database Structure

- "Database info"
- "Database structure"
- "What collections are in the database?"
- "Show me database information"

**What you'll get:**
- List of all collections
- Statistics for each collection
- Collection names and document counts

### Collection Summary

Get detailed summary of a specific collection:

- "Summary of users collection"
- "Statistics for logs collection"
- "Stats for analytics collection"

**What you'll get:**
- Total document count
- Field information
- Sample data structure

---

## Examples

### Example 1: Basic Count
**Question:** "How many users are in the database?"
**Response:** Total count of users

### Example 2: Group Query
**Question:** "Group users by site"
**Response:** List of sites with user counts and user details

### Example 3: Date Range
**Question:** "Logs per day since November first"
**Response:** Daily breakdown of logs with counts and details

### Example 4: Analytics Summary
**Question:** "Analytics summary"
**Response:** Overall statistics including total records, unique users, action types

### Example 5: Files Sent
**Question:** "How many files have been sent using the analytics collection?"
**Response:** Total count of successfully sent files

### Example 6: Specific Collection Count
**Question:** "Number of records in each collection"
**Response:** Count for all collections (users, sites, logs, analytics, job numbers)

### Example 7: Job Numbers by Language
**Question:** "Job numbers by language"
**Response:** Breakdown showing count of job numbers per language

### Example 8: Last Job Numbers Created
**Question:** "Can I see the last 100 job numbers created?"
**Response:** List of the 100 most recently created job numbers, sorted by creation date (most recent first), showing job number value, document symbol, language, and creation date

### Example 9: Analytics by Action
**Question:** "Analytics grouped by action"
**Response:** Count of analytics records per action type

---

## Query Patterns

The chatbot recognizes these patterns:

### Count Patterns
- "how many [collection]"
- "count [collection]"
- "number of [collection]"
- "total [collection]"

### Group Patterns
- "[entity] grouped by [field]"
- "group [entity] by [field]"
- "[entity] by [field]"

### Date Patterns
- "since [month] [day]"
- "from [month] [day]"
- "per day since [date]"
- "by day from [date]"

### Summary Patterns
- "[collection] summary"
- "[collection] statistics"
- "[collection] stats"

---

## Important Notes

1. **Read-Only Operations:** All queries are read-only. No data is modified, created, or deleted.

2. **Case Insensitive:** Queries are case-insensitive. "Users" and "users" work the same.

3. **Natural Language:** You can ask questions in natural language. The chatbot will interpret your intent.

4. **Multiple Queries:** You can combine concepts (e.g., "analytics per day since November first")

5. **Limits:** Results are limited to prevent overwhelming responses:
   - Default: 50-100 records
   - Date ranges: Up to 1000 records
   - Group queries: Up to 50-100 groups

6. **Date Formats:** The chatbot understands:
   - Month names: "November", "Nov", "December", "Dec", etc.
   - Day numbers: "1st", "1", "15", etc.
   - Defaults to current year if not specified

---

## Troubleshooting

### If you don't get a response:

1. **Check your query keywords:** Make sure you're using recognized terms (users, sites, logs, analytics, job numbers)

2. **Try simpler queries:** Start with basic counts like "How many users?"

3. **Be specific:** For group queries, specify both the entity and grouping field

4. **Check spelling:** While queries are flexible, ensure collection names are correct

### Common Issues:

- **"No response"**: Try rephrasing or using simpler language
- **"Too much data"**: The response may be truncated. Try more specific queries
- **"Wrong results"**: Be more specific about what you're looking for

---

## Quick Reference

| Query Type | Example |
|------------|---------|
| Count | "How many users?" |
| List | "Show me all sites" |
| Group | "Users grouped by site" |
| Date Range | "Logs since November 1st" |
| Per Day | "Logs per day since November first" |
| Summary | "Analytics summary" |
| Action Types | "Analytics action types" |
| Files Sent | "How many files have been sent?" |
| By Field | "Job numbers by language" |

---

**Last Updated:** 2025-11-13

For more information about the database schema, see the ODS Actions documentation.

