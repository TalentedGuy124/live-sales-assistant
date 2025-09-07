# retriever_agent.py (Original Code for v3)

import redis
import json
import time
import weaviate

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Retriever Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Retriever Agent: Could not connect to Redis. Error: {e}")
    exit()

# Connect to Weaviate using the original v3 client
try:
    client = weaviate.Client("http://localhost:8080")
    if client.is_ready():
        print("Retriever Agent: Successfully connected to Weaviate.")
    else:
        print("Retriever Agent: Could not connect to Weaviate. Please ensure it is running.")
        exit()
except Exception as e:
    print(f"Retriever Agent: Could not connect to Weaviate. Error: {e}")
    exit()

# --- NOTE on Weaviate Data ---
# Our Weaviate database is EMPTY. This agent will connect to it,
# but it will not find any documents. We are simulating a search.
# ---

def search_internal_documents(query: str):
    """
    This function searches the Weaviate vector database.
    NOTE: It will not find anything yet as the DB is empty. We are returning fake data.
    """
    print(f"Retriever Agent: Searching internal documents for '{query}'...")
    
    # This is the query method for v3 of the client
    # response = (
    #     client.query
    #     .get("Document", ["content", "source"])
    #     .with_near_text({"concepts": [query]})
    #     .with_limit(2)
    #     .do()
    # )
    # real_results = response["data"]["Get"]["Document"]
    
    time.sleep(1) # Simulate search time
    return [
        {
            "content": f"Our case study shows that {query} can be solved using our 'Innovate' product package, increasing efficiency by 30%.",
            "source": "internal_doc_case_study_045.pdf"
        },
    ]

# --- Main Agent Loop ---
print("Retriever Agent: Listening for company entities on 'entity_stream'...")

consumer_name = "retriever_consumer_1"
group_name = "retriever_group"
stream_name = "entity_stream"

try:
    r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
except redis.exceptions.ResponseError:
    pass # Group already exists

while True:
    try:
        messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=0)
        
        if messages:
            message_id, message_data = messages[0][1][0]
            data = json.loads(message_data["data"])
            
            if data.get("entity_type") == "company":
                entity_name = data["entity_name"]
                retrieved_docs = search_internal_documents(entity_name)
                
                if retrieved_docs:
                    event = {
                        "agent_id": "retriever_agent",
                        "timestamp": time.time(),
                        "session_id": data["session_id"],
                        "query": entity_name,
                        "results": retrieved_docs,
                        "confidence": 0.85,
                        "sources": [doc['source'] for doc in retrieved_docs]
                    }
                    r.xadd("intelligence_stream", {"data": json.dumps(event)})
                    print(f"Retriever Agent: Found internal docs for '{entity_name}'. Published to 'intelligence_stream'.")

            r.xack(stream_name, group_name, message_id)

    except Exception as e:
        print(f"Retriever Agent: An error occurred: {e}")
        time.sleep(5)