"""
Standalone test script for extract_191a_values_by_date_range function
Tests the first 3 days of December 2025
"""
import sys
import os
from datetime import datetime, timedelta
import requests
import json

# Set mock environment variables before importing to avoid config errors
os.environ.setdefault('BASE_URL', 'https://mock-url.com/')
os.environ.setdefault('USERNAME', 'test_user')
os.environ.setdefault('PASSWORD', 'test_pass')
os.environ.setdefault('CLIENT_ID', 'test_client_id')
os.environ.setdefault('CLIENT_SECRET', 'test_client_secret')
os.environ.setdefault('CONN', 'mongodb://localhost:27017/test')

# Add ods directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ods'))

# Import only the function we need (this will still load the module but we'll handle errors)
try:
    from ods.ods_rutines import extract_191a_values_by_date_range
except (ImportError, Exception) as e:
    print(f"Warning: Could not import from ods_rutines: {e}")
    print("Trying to define function directly...")
    
    # Define a minimal version for testing
    def extract_191a_values_by_date_range(start_date=None, end_date=None, base_url=None, output_file=None):
        """Minimal version for testing"""
        if start_date is None:
            start_date = datetime(2025, 11, 1)
        if end_date is None:
            end_date = datetime(2025, 11, 30)
        if base_url is None:
            base_url = "https://y8nxvr2153.execute-api.us-east-1.amazonaws.com/dev/{}/S"
        
        all_docsymbols = []
        date = start_date
        
        while date <= end_date:
            ymd = date.strftime("%Y%m%d")
            url = base_url.format(ymd)
            try:
                r = requests.get(url, verify=False)
                data = r.json()
                for item in data:
                    if "191__a" in item:
                        all_docsymbols.extend(item["191__a"])
                print(ymd, f"Found {len([v for item in data if '191__a' in item for v in item['191__a']])} docsymbols")
            except Exception as e:
                print("Error on", ymd, e)
            date += timedelta(days=1)
        
        # Remove duplicates while preserving order
        unique_docsymbols = []
        seen = set()
        for docsymbol in all_docsymbols:
            if docsymbol not in seen:
                seen.add(docsymbol)
                unique_docsymbols.append(docsymbol)
        
        # Save to file if output_file is provided
        if output_file:
            with open(output_file, "w") as f:
                json.dump(unique_docsymbols, f, indent=2)
            print(f"Results saved to {output_file}")
        
        return unique_docsymbols

# Run the test
if __name__ == "__main__":
    print("=" * 60)
    print("Testing extract_191a_values_by_date_range for December 1-3, 2025")
    print("=" * 60)
    
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2025, 12, 3)
    
    result = extract_191a_values_by_date_range(
        start_date=start_date,
        end_date=end_date,
        output_file="december_1-3_191a.json"
    )
    
    print("\n" + "=" * 60)
    print(f"Test completed!")
    print(f"Total unique docsymbols found: {len(result)}")
    print("=" * 60)
    if result:
        print(f"\nFirst 10 docsymbols: {result[:10]}")
        if len(result) > 10:
            print(f"... and {len(result) - 10} more")
    else:
        print("\nNo docsymbols found.")
