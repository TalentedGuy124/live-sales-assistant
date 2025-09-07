# domain_agent.py

import redis
import json
import time

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Domain Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Domain Agent: Could not connect to Redis. Error: {e}")
    exit()

# --- Placeholder for a real data enrichment API ---
def fetch_company_data(company_name: str):
    """
    This is a placeholder function. In a real-world application, this function
    would make an API call to a service like Clearbit, Crunchbase, or a
    custom web scraper to get real data about the company.

    For this prototype, we will return some realistic-looking fake data.
    """
    print(f"Domain Agent: Fetching intelligence for '{company_name}'...")
    # Simulate the time it takes to make a real API call
    time.sleep(1.5) 
    
    # Return a structured dictionary of fake data
    # Notice we include a 'source_url' to maintain provenance
    return {
        "overview": f"{company_name} is a fictional market leader in innovative solutions for the tech industry.",
        "employee_size": "1,001-5,000 employees",
        "recent_news": f"'{company_name}' recently announced a partnership with a major cloud provider.",
        "source_url": "https://www.fake-business-news.com/story/123"
    }
# --- End of placeholder ---

# --- Main Agent Loop ---
print("Domain Agent: Listening for company entities on 'entity_stream'...")

consumer_name = "domain_consumer_1"
group_name = "domain_group"
stream_name = "entity_stream"

try:
    r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    print(f"Domain Agent: Consumer group '{group_name}' created.")
except redis.exceptions.ResponseError:
    print(f"Domain Agent: Consumer group '{group_name}' already exists.")

while True:
    try:
        messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=0)
        
        if messages:
            message_id, message_data = messages[0][1][0]
            data = json.loads(message_data["data"])
            
            # This agent only cares about entities of type 'company'
            if data.get("entity_type") == "company":
                entity_name = data["entity_name"]
                
                # Fetch the company intelligence using our placeholder function
                company_info = fetch_company_data(entity_name)
                
                # Create a new event with the enriched data
                event = {
                    "agent_id": "domain_agent",
                    "timestamp": time.time(),
                    "session_id": data["session_id"],
                    "company_name": entity_name,
                    "data": company_info,
                    "confidence": 0.9, # Confidence score for the data
                    "sources": [company_info["source_url"]] # Source for provenance
                }
                
                # Publish the enriched data to the 'intelligence_stream'
                # The Planner agent will listen to this stream later.
                r.xadd("intelligence_stream", {"data": json.dumps(event)})
                print(f"Domain Agent: Fetched info for '{entity_name}'. Published to 'intelligence_stream'.")

            r.xack(stream_name, group_name, message_id)

    except Exception as e:
        print(f"Domain Agent: An error occurred: {e}")
        time.sleep(5)