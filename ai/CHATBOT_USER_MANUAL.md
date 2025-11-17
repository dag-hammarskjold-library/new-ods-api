# ODS Actions Chatbot - Complete User Manual

Welcome to the ODS Actions Chatbot! This AI-powered assistant helps you understand and use the ODS Actions application, and query the odsActions database. The chatbot uses Google's Gemini AI to provide intelligent, context-aware responses.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Application Features & Usage](#application-features--usage)
4. [Database Queries](#database-queries)
5. [Query Examples](#query-examples)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is the ODS Actions Chatbot?

The ODS Actions Chatbot is an intelligent assistant that can:
- Answer questions about the ODS Actions application features and usage
- Query the odsActions MongoDB database (read-only)
- Provide step-by-step instructions
- Explain system architecture and technical details
- Help with troubleshooting

### Key Features

- **Natural Language Processing**: Ask questions in plain English
- **Context-Aware**: Understands the ODS Actions domain
- **Database Integration**: Can query and analyze database information
- **Read-Only Database Access**: Safe queries that never modify data
- **Comprehensive Knowledge**: Knows about application features, database structure, and workflows

---

## Getting Started

### How to Use the Chatbot

1. **Access the Chatbot**: The chatbot is available in the ODS Actions web interface
2. **Type Your Question**: Enter your question in natural language
3. **Get Instant Answers**: Receive detailed, context-aware responses

### Basic Usage Tips

- **Be Specific**: More specific questions get better answers
- **Use Natural Language**: No need for special syntax or commands
- **Ask Follow-ups**: The chatbot maintains context during conversation
- **Try Different Phrasings**: If one question doesn't work, try rephrasing

---

## Application Features & Usage

The chatbot can answer questions about all ODS Actions features. Here's what you can ask about:

### 1. Display Metadata Tab

**What it does:** Search and display metadata for document symbols

**Questions you can ask:**
- "How do I display metadata for a document symbol?"
- "What is the Display Metadata tab used for?"
- "How to search for document symbols?"
- "What information is shown in the metadata table?"

**Features:**
- Input: Textarea for entering document symbols (one per line)
- Output: Responsive table with columns:
  - Document Symbol
  - Agenda
  - Session
  - Distribution
  - Area
  - Subjects
  - Job Number
  - Title
  - Publication Date
  - Release Date
- Export: CSV export functionality
- Validation: Button disabled when input is empty

### 2. Send Metadata Tab

**What it does:** Send document metadata to the ODS system

**Questions you can ask:**
- "How do I send metadata to ODS?"
- "What happens when I send metadata?"
- "How to create or update metadata in ODS?"
- "What is the Send Metadata tab?"

**Features:**
- Input: Textarea for entering document symbols
- Processing: Creates or updates metadata in ODS
- Output: Submission results (created/updated/error messages)
- Export: CSV export of submission results
- Validation: Real-time input validation

**Process:**
1. Metadata is retrieved from Central Database
2. Job numbers are automatically generated if needed
3. Only English title is sent (other languages have empty titles)

### 3. Send Files Tab

**What it does:** Upload files associated with document symbols to ODS

**Questions you can ask:**
- "How do I send files to ODS?"
- "What is the Send Files tab?"
- "How are files uploaded?"
- "What languages are supported for file uploads?"

**Features:**
- Input: Textarea for entering document symbols
- Processing: Downloads files from Central Database and uploads to ODS
- Output: Upload results for each language (AR, ZH, EN, FR, RU, ES, DE)
- Progress tracking and result management
- Export: CSV export of upload results

**Process:**
1. Validates document symbol exists in ODS
2. Downloads files from Central Database for all 7 languages
3. Uploads files to ODS with corresponding job numbers
4. Updates release dates if needed
5. Releases unused job numbers
6. Cleans temporary files

**Supported Languages:**
- AR (Arabic) - Index 0
- ZH (Chinese) - Index 1
- EN (English) - Index 2
- FR (French) - Index 3
- RU (Russian) - Index 4
- ES (Spanish) - Index 5
- DE (German) - Index 6

### 4. Parameters Tab (Admin Only)

**What it does:** System administration features

**Questions you can ask:**
- "How do I manage sites?"
- "How to create a new user?"
- "How to view system logs?"
- "What permissions can I set for users?"

**Features:**

**Site Management:**
- Add sites with code (3-letter), label, and prefix (2-letter)
- Example: Code "NYC", Label "New York", Prefix "NX"

**User Management:**
- Create users with site assignment
- Set tab permissions:
  - Display Metadata tab
  - Create/Update Metadata tab
  - Send Files tab
  - Job Numbers tab
  - Parameters tab

**System Logs:**
- View and export activity logs
- Filter by user, action, or date
- Export logs to CSV

### 5. Change Password Tab

**What it does:** User password management

**Questions you can ask:**
- "How do I change my password?"
- "What are the password requirements?"

**Features:**
- Email: Pre-filled with current user email
- New Password: Input field with validation (minimum 6 characters)
- Confirm Password: Confirmation field
- Validation: Ensures passwords match before submission
- Password is hashed before storage

---

## Database Queries

The chatbot can query the odsActions MongoDB database. **All queries are READ-ONLY** - no modifications, creations, or deletions are performed.

### Database Collections

The database contains 6 main collections:

1. **Users Collection** (`ods_actions_users_collection`)
   - User accounts with permissions
   - Site assignments
   - Tab access permissions

2. **Sites Collection** (`ods_actions_sites_collection`)
   - Site configurations
   - Site codes and labels
   - Job number prefixes

3. **Logs Collection** (`ods_actions_logs_collection`)
   - System activity logs
   - User actions
   - Timestamps

4. **Analytics Collection** (`ods_actions_analytics_collection`)
   - Detailed analytics data
   - Operation results
   - Action tracking

5. **Job Numbers Collection** (`ods_actions_jobnumbers_collection`)
   - Job number tracking
   - Document symbol associations
   - Language mappings

6. **ODS Job Number Collection** (`ods_jobnumber_collection`)
   - Released/unused job numbers

---

### Basic Database Queries

#### Get Collection Counts

**Ask:**
- "How many records in each collection?"
- "Number of records in all collections"
- "Count of all collections"
- "Show me record counts for all collections"

**Response:** Count for each collection

#### Get Specific Collection Count

**Ask:**
- "How many users?"
- "Number of sites"
- "Count of logs"
- "How many analytics records?"
- "Total job numbers"

**Response:** Total count for the specified collection

---

### Collection-Specific Queries

#### Users Collection

**Query Users:**
- "Show me all users"
- "List users"
- "Find user with email [email@example.com]"
- "Users from site [SITE]"

**What you get:**
- User email
- Site assignment
- Permissions (show_display, show_create_update, show_send_file, show_jobnumbers_management, show_parameters)
- Creation date

#### Sites Collection

**Query Sites:**
- "Show me all sites"
- "List sites"
- "What sites are available?"

**What you get:**
- Site code (3-letter)
- Site label/name
- Prefix for job numbers (2-letter)
- Creation date

#### Logs Collection

**Query Logs:**
- "Show me recent logs"
- "List logs"
- "What are the recent activities?"

**What you get:**
- User who performed the action
- Action description
- Date/timestamp

#### Analytics Collection

**Query Analytics:**
- "Show me analytics"
- "List analytics"
- "Recent analytics data"

**What you get:**
- User email
- Action type (e.g., "send_file_endpoint", "loading_symbol_endpoint")
- Date/timestamp
- Detailed operation results (data array)

#### Job Numbers Collection

**Query Job Numbers:**
- "Show me job numbers"
- "List job numbers"
- "Find job numbers for document symbol [A/RES/68/123]"
- "Job numbers for [NX900000]"
- "Last 100 job numbers created"
- "Recent 50 job numbers"
- "Show me the last job numbers created"
- "Total job numbers"
- "How many job numbers?"

**What you get:**
- Job number value
- Associated document symbol
- Language code (AR, ZH, EN, FR, RU, ES, DE)
- Creation date

**Notes:**
- When asking for "total job numbers" or "how many job numbers", you'll get the actual count of all job numbers in the database
- When asking for "last" or "recent" job numbers, you can specify a number (e.g., "last 100") or use the default of 100. Results are sorted by creation date with the most recent first

---

### Group/Aggregation Queries

Group queries organize data by specific fields and provide counts and statistics.

#### Group Users by Site

**Ask:**
- "Group users by site"
- "Users grouped by site"
- "Show me users organized by site"

**What you get:**
- Site name
- Number of users per site
- List of users in each site with their permissions

#### Group Logs by User

**Ask:**
- "Logs grouped by user"
- "Group logs by user"
- "Show me logs per user"

**What you get:**
- User email
- Number of logs per user
- Latest and earliest log dates

#### Group Logs by Action

**Ask:**
- "Logs grouped by action"
- "Group logs by action type"
- "Show me logs by action"

**What you get:**
- Action type
- Count of logs per action
- Latest and earliest log dates

#### Group Job Numbers by Language

**Ask:**
- "Job numbers by language"
- "Group job numbers by language"
- "Job numbers grouped by language"

**What you get:**
- Language code (AR, ZH, EN, FR, RU, ES, DE)
- Count of job numbers per language
- Date ranges

#### Group Job Numbers by Document Symbol

**Ask:**
- "Job numbers by document symbol"
- "Group job numbers by docsymbol"
- "Job numbers grouped by document symbol"

**What you get:**
- Document symbol
- Count of job numbers per symbol
- Languages associated with each symbol

#### Group Analytics by Action

**Ask:**
- "Analytics grouped by action"
- "Group analytics by action type"
- "Analytics by action"

**What you get:**
- Action type
- Count of analytics records per action
- Date ranges

#### Group Analytics by User

**Ask:**
- "Analytics grouped by user"
- "Group analytics by user"
- "Analytics by user"

**What you get:**
- User email
- Count of analytics records per user
- Unique action types per user
- Date ranges

#### Group Analytics by Action and User

**Ask:**
- "Analytics by action and user"
- "Group analytics by action and user"
- "Analytics grouped by action and user"

**What you get:**
- Action type and user combination
- Count for each combination
- Date ranges

---

### Date Range Queries

Query data within specific date ranges or grouped by day.

#### Logs by Date Range

**Ask:**
- "Logs since November 1st"
- "Logs from November 1"
- "Show me logs since Nov 1"

**What you get:** All logs from the specified date to now

#### Logs Per Day

**Ask:**
- "Logs per day since November first"
- "Logs by day since November 1st"
- "Logs each day from November 1"

**What you get:**
- Date (YYYY-MM-DD)
- Number of logs per day
- List of logs for each day

#### Analytics by Date Range

**Ask:**
- "Analytics since November 1st"
- "Analytics from November 1"
- "Show me analytics since Nov 1"

**What you get:** All analytics records from the specified date to now

#### Analytics Per Day

**Ask:**
- "Analytics per day since November first"
- "Analytics by day since November 1st"
- "Analytics each day from November 1"

**What you get:**
- Date (YYYY-MM-DD)
- Number of analytics records per day
- Unique users and actions per day
- List of analytics for each day

**Date Format Support:**
- Month names: "November", "Nov", "December", "Dec", etc.
- Day numbers: "1st", "1", "15", etc.
- Defaults to current year if not specified

---

### Analytics-Specific Queries

#### Analytics Summary

**Ask:**
- "Analytics summary"
- "Analytics statistics"
- "Analytics stats"
- "Summary of analytics collection"

**What you get:**
- Total records
- Unique user count
- Unique action count
- List of all action types
- Earliest and latest dates

#### Analytics Action Types

**Ask:**
- "Analytics action types"
- "What action types are in analytics?"
- "List analytics action types"
- "Types of actions in analytics"

**What you get:**
- List of all unique action types:
  - `send_file_endpoint` - File upload operations
  - `loading_symbol_endpoint` - Metadata loading operations
  - `create_metadata_ods` - Metadata creation/update operations
  - And other action types

#### Files Sent Count

**Ask:**
- "How many files have been sent?"
- "Count files sent using analytics"
- "Number of files sent"
- "How many files have been sent using the analytics collection?"

**What you get:**
- Total number of files successfully sent
- Breakdown by action type (if detailed query)

**How it works:**
- Looks for analytics records with action `send_file_endpoint`
- Counts successful file sends from the data array
- Only counts files with result "downloaded and sent successfully!!!"

---

### Database Information Queries

#### Database Structure

**Ask:**
- "Database info"
- "Database structure"
- "What collections are in the database?"
- "Show me database information"

**What you get:**
- List of all collections
- Statistics for each collection
- Collection names and document counts

#### Collection Summary

**Ask:**
- "Summary of users collection"
- "Statistics for logs collection"
- "Stats for analytics collection"

**What you get:**
- Total document count
- Field information
- Sample data structure

---

## Query Examples

### Example 1: Application Feature Question
**Question:** "How do I display metadata for a document symbol?"
**Response:** Step-by-step instructions for using the Display Metadata tab

### Example 2: Basic Count
**Question:** "How many users are in the database?"
**Response:** Total count of users

### Example 3: Group Query
**Question:** "Group users by site"
**Response:** List of sites with user counts and user details

### Example 4: Date Range
**Question:** "Logs per day since November first"
**Response:** Daily breakdown of logs with counts and details

### Example 5: Analytics Summary
**Question:** "Analytics summary"
**Response:** Overall statistics including total records, unique users, action types

### Example 6: Files Sent
**Question:** "How many files have been sent using the analytics collection?"
**Response:** Total count of successfully sent files

### Example 7: Specific Collection Count
**Question:** "Number of records in each collection"
**Response:** Count for all collections (users, sites, logs, analytics, job numbers)

### Example 8: Job Numbers by Language
**Question:** "Job numbers by language"
**Response:** Breakdown showing count of job numbers per language

### Example 9: Last Job Numbers Created
**Question:** "Can I see the last 100 job numbers created?"
**Response:** List of the 100 most recently created job numbers, sorted by creation date (most recent first), showing job number value, document symbol, language, and creation date

### Example 10: Analytics by Action
**Question:** "Analytics grouped by action"
**Response:** Count of analytics records per action type

### Example 11: Application Workflow
**Question:** "How do I send files to ODS?"
**Response:** Complete workflow explanation for the Send Files tab

---

## Tips & Best Practices

### Asking Effective Questions

1. **Be Specific**
   - ✅ "How many users are in the database?"
   - ❌ "Tell me about users"

2. **Use Clear Language**
   - ✅ "Group logs by user"
   - ❌ "logs user group"

3. **Combine Concepts**
   - ✅ "Analytics per day since November first"
   - ✅ "Logs grouped by action since November 1st"

4. **Ask Follow-up Questions**
   - The chatbot maintains context, so you can ask:
     - "Show me more details"
     - "What about sites?"
     - "Can you group that by user?"

### Query Optimization

1. **For Counts:** Use "how many" or "count" for faster responses
2. **For Details:** Be specific about what information you need
3. **For Large Datasets:** Use date ranges or grouping to get manageable results
4. **For Analytics:** Use summary queries for overview, detailed queries for specifics

### Understanding Responses

- **Count Queries:** Return numbers quickly
- **List Queries:** Return formatted data with details
- **Group Queries:** Return organized, aggregated data
- **Summary Queries:** Return statistics and overviews

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "No response" or "Response was blocked"

**Solutions:**
- Try rephrasing your question
- Break complex questions into smaller parts
- Use simpler language
- Check if your question contains database keywords

#### Issue: "Response was truncated"

**Solutions:**
- Ask for counts instead of full data
- Use date ranges to limit results
- Request summaries instead of detailed lists
- Break your query into multiple smaller questions

#### Issue: "Wrong results" or "Not what I expected"

**Solutions:**
- Be more specific about what you're looking for
- Use collection names explicitly (e.g., "analytics collection")
- Check your spelling and terminology
- Try different phrasings

#### Issue: "Analytics queries not working"

**Solutions:**
- Make sure you mention "analytics" in your question
- Try "analytics summary" or "how many analytics records"
- Use specific queries like "analytics by action"
- Check if you're asking about the right collection

### Getting Help

If you're having trouble:
1. Try simpler questions first
2. Check the examples in this manual
3. Use the query patterns listed below
4. Be specific about what you need

---

## Query Patterns Reference

### Count Patterns
- "how many [collection]"
- "count [collection]"
- "number of [collection]"
- "total [collection]"

### List Patterns
- "show me [collection]"
- "list [collection]"
- "find [entity]"

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

## Application Architecture Questions

The chatbot can also answer questions about the application architecture:

### Technology Stack

**Ask:**
- "What technologies does ODS Actions use?"
- "What is the frontend built with?"
- "What database does it use?"

**Response:** Information about Vue.js, Flask, MongoDB, etc.

### API Endpoints

**Ask:**
- "What API endpoints are available?"
- "How does authentication work?"
- "What is the /loading_symbol endpoint?"

**Response:** Details about REST API endpoints and their usage

### Workflows

**Ask:**
- "How does file upload work?"
- "What is the process for sending metadata?"
- "How are job numbers generated?"

**Response:** Step-by-step workflow explanations

---

## Security & Permissions

### User Permissions

**Ask:**
- "What permissions can users have?"
- "How are permissions set?"
- "What is the permission system?"

**Response:** Information about tab-level access control

### Authentication

**Ask:**
- "How does login work?"
- "How are passwords stored?"
- "What is session management?"

**Response:** Details about authentication and security features

---

## Quick Reference Card

### Application Features
| Feature | Ask About |
|---------|-----------|
| Display Metadata | "How do I display metadata?" |
| Send Metadata | "How to send metadata to ODS?" |
| Send Files | "How do I upload files?" |
| User Management | "How to create a user?" |
| Site Management | "How to add a site?" |
| Logs | "How to view system logs?" |

### Database Queries
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

### Common Questions
- "How do I [feature]?" - Get step-by-step instructions
- "What is [feature]?" - Get feature explanation
- "How many [collection]?" - Get count
- "[Entity] grouped by [field]" - Get grouped data
- "[Collection] summary" - Get statistics

---

## Important Notes

### Read-Only Database Access

⚠️ **All database queries are READ-ONLY**
- No data is modified
- No records are created
- No records are deleted
- Safe to query anytime

### Response Limits

- Default queries: 50-100 records
- Date range queries: Up to 1000 records
- Group queries: Up to 50-100 groups
- Large results may be truncated with a note

### Date Handling

- Understands month names: "November", "Nov", "December", "Dec", etc.
- Understands day numbers: "1st", "1", "15", etc.
- Defaults to current year if year not specified
- Supports formats: "since November 1st", "from Nov 1", etc.

### Language Support

The system supports 7 official languages:
- AR (Arabic) - Index 0
- ZH (Chinese) - Index 1
- EN (English) - Index 2
- FR (French) - Index 3
- RU (Russian) - Index 4
- ES (Spanish) - Index 5
- DE (German) - Index 6

---

## Advanced Topics

### Understanding Analytics Data

Analytics records contain:
- **user**: User email who performed the action
- **action**: Action type (e.g., "send_file_endpoint")
- **date**: Timestamp of the action
- **data**: Array of operation results

For file sends, the data array contains:
- List of file operation results
- Each result has: filename, docsymbol, language, jobnumber, result
- Success indicator: "downloaded and sent successfully!!!"

### Job Number System

Job numbers are:
- Generated with site-specific prefixes (e.g., "NX900000")
- Associated with document symbols
- Mapped to languages (AR=0, ZH=1, EN=2, FR=3, RU=4, ES=5, DE=6)
- Tracked in the job numbers collection

### File Upload Process

When files are sent:
1. Document symbol is validated in ODS
2. Files are downloaded from Central Database (CDB)
3. Files are uploaded to ODS with job numbers
4. Release dates are updated if needed
5. Unused job numbers are released
6. Temporary files are cleaned
7. Results are stored in analytics collection

---

## Conclusion

The ODS Actions Chatbot is a powerful tool for:
- Learning about the application
- Getting help with features
- Querying the database
- Understanding system workflows
- Analyzing data and statistics

Remember:
- Ask questions in natural language
- Be specific for better results
- Use the examples as a guide
- All database queries are safe (read-only)

**Happy querying!**

---

**Last Updated:** 2025-11-13  
**Version:** 1.0

For technical details about the database schema, see the ODS Actions technical documentation.

