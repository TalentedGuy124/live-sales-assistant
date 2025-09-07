# planner_agent.py

import redis
import json
import time

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Planner Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Planner Agent: Could not connect to Redis. Error: {e}")
    exit()

# --- Placeholder for a real LLM (like GPT or Claude) ---
def generate_talking_points(intelligence_data: dict):
    """
    This is a placeholder for a real Large Language Model (LLM).
    In a full application, we would send the collected intelligence to an LLM
    with a prompt like "Based on this data, suggest three talking points for a
    salesperson."

    For this prototype, we'll use simple rules and templates to simulate the LLM's
    output. This is fast, free, and demonstrates the logic.
    """
    agent_id = intelligence_data.get("agent_id")
    suggestions = []

    if agent_id == "domain_agent":
        company_name = intelligence_data.get("company_name")
        news = intelligence_data.get("data", {}).get("recent_news")
        # Rule 1: If we have recent news, create a talking point about it.
        if news:
            point = f"Mention their recent news: '{news}' to build rapport."
            suggestions.append({"point": point, "confidence": 0.8, "sources": intelligence_data["sources"]})

    elif agent_id == "retriever_agent":
        query = intelligence_data.get("query")
        results = intelligence_data.get("results", [])
        # Rule 2: If our internal documents mention the company, create a talking point.
        if results:
            source_doc = results[0]["source"] # Get the first document source
            point = f"We have a case study mentioning '{query}'. Highlight how we solved a similar problem. See '{source_doc}'."
            suggestions.append({"point": point, "confidence": 0.9, "sources": intelligence_data["sources"]})
    
    # A generic suggestion if no other rules match
    if not suggestions:
        suggestions.append({"point": "Ask an open-ended question about their current challenges.", "confidence": 0.7, "sources": ["General Sales Strategy"]})

    print(f"Planner Agent: Generated {len(suggestions)} talking point(s).")
    return suggestions

# --- Main Agent Loop ---
print("Planner Agent: Listening for intelligence on 'intelligence_stream'...")

consumer_name = "planner_consumer_1"
group_name = "planner_group"
stream_name = "intelligence_stream"

try:
    r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    print(f"Planner Agent: Consumer group '{group_name}' created.")
except redis.exceptions.ResponseError:
    print(f"Planner Agent: Consumer group '{group_name}' already exists.")

while True:
    try:
        messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=0)
        
        if messages:
            message_id, message_data = messages[0][1][0]
            data = json.loads(message_data["data"])
            
            # Generate talking points based on the received intelligence
            talking_points = generate_talking_points(data)
            
            if talking_points:
                event = {
                    "agent_id": "planner_agent",
                    "timestamp": time.time(),
                    "session_id": data["session_id"],
                    "suggestions": talking_points
                }
                
                # Publish the suggestions to the 'suggestion_stream'
                # The Ranking agent will listen to this stream next.
                r.xadd("suggestion_stream", {"data": json.dumps(event)})
                print(f"Planner Agent: Published suggestions to 'suggestion_stream'.")

            r.xack(stream_name, group_name, message_id)

    except Exception as e:
        print(f"Planner Agent: An error occurred: {e}")
        time.sleep(5)