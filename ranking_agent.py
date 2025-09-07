# ranking_agent.py

import redis
import json
import time

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Ranking Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Ranking Agent: Could not connect to Redis. Error: {e}")
    exit()

# --- Ranking Logic ---
def rank_suggestions(suggestions: list):
    """
    Ranks suggestions based on a set of rules.
    In a real system, this could be a complex algorithm or another LLM call.

    For our prototype, we'll use a simple rule: rank by the 'confidence'
    score we assigned in the Planner Agent, from highest to lowest.
    """
    print(f"Ranking Agent: Ranking {len(suggestions)} suggestion(s)...")
    # The 'key' is a function that tells sort() which value to use for sorting.
    # 'reverse=True' means it will sort from highest to lowest.
    ranked_list = sorted(suggestions, key=lambda s: s['confidence'], reverse=True)
    return ranked_list

# --- Main Agent Loop ---
print("Ranking Agent: Listening for suggestions on 'suggestion_stream'...")

consumer_name = "ranking_consumer_1"
group_name = "ranking_group"
stream_name = "suggestion_stream"

try:
    r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    print(f"Ranking Agent: Consumer group '{group_name}' created.")
except redis.exceptions.ResponseError:
    print(f"Ranking Agent: Consumer group '{group_name}' already exists.")

while True:
    try:
        messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=0)
        
        if messages:
            message_id, message_data = messages[0][1][0]
            data = json.loads(message_data["data"])
            
            suggestions = data.get("suggestions", [])
            
            if suggestions:
                # Rank the suggestions using our logic
                ranked_suggestions = rank_suggestions(suggestions)
                
                event = {
                    "agent_id": "ranking_agent",
                    "timestamp": time.time(),
                    "session_id": data["session_id"],
                    "ranked_suggestions": ranked_suggestions
                }
                
                # Publish the final, ranked list to its own stream
                # The UI Agent will listen to this final stream.
                r.xadd("ranked_suggestion_stream", {"data": json.dumps(event)})
                print(f"Ranking Agent: Published ranked suggestions to 'ranked_suggestion_stream'.")
                # For debugging, let's print the top suggestion
                print(f"Ranking Agent: Top suggestion is: '{ranked_suggestions[0]['point']}'")


            r.xack(stream_name, group_name, message_id)

    except Exception as e:
        print(f"Ranking Agent: An error occurred: {e}")
        time.sleep(5)