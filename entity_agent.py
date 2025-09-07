# entity_agent.py

import redis
import json
import spacy
import time

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Entity Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Entity Agent: Could not connect to Redis. Error: {e}")
    exit()

# Load the spaCy model we downloaded
try:
    nlp = spacy.load("en_core_web_sm")
    print("Entity Agent: spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    print("Entity Agent: spaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
    exit()

# --- Main Agent Loop ---
print("Entity Agent: Listening for transcripts on 'stt_stream'...")

# We need a unique consumer name for this agent
consumer_name = "entity_consumer_1"
group_name = "entity_group"
stream_name = "stt_stream"

# Create the consumer group. If it already exists, this will do nothing.
try:
    r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    print(f"Entity Agent: Consumer group '{group_name}' created for stream '{stream_name}'.")
except redis.exceptions.ResponseError:
    print(f"Entity Agent: Consumer group '{group_name}' already exists.")

while True:
    try:
        # Wait for a new message in the stream.
        # The 'block=0' means it will wait forever until a message arrives.
        messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=0)
        
        if messages:
            # messages is a list of streams, and each stream has a list of messages
            # We are only listening to one stream and asking for one message
            message_id, message_data = messages[0][1][0]
            
            # The actual message content is in the 'data' field
            data = json.loads(message_data["data"])
            transcript = data["transcript"]
            session_id = data["session_id"]
            
            print(f"\nEntity Agent: Received transcript: '{transcript}'")
            
            # Process the transcript with spaCy to find named entities
            doc = nlp(transcript)
            
            # We are looking for organizations (companies, competitors, etc.)
            entities = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            
            if entities:
                for entity in entities:
                    # Create a new event for each entity found
                    event = {
                        "agent_id": "entity_agent",
                        "timestamp": time.time(),
                        "session_id": session_id,
                        "entity_name": entity,
                        "entity_type": "company", # We could also detect 'person', 'product', etc.
                        "source_transcript": transcript
                    }
                    
                    # Publish the new event to the 'entity_stream'
                    # The Domain and Retriever agents will listen to this stream.
                    r.xadd("entity_stream", {"data": json.dumps(event)})
                    print(f"Entity Agent: Found company '{entity}'. Published event to 'entity_stream'.")
            else:
                print("Entity Agent: No company entities found in this transcript.")

            # Acknowledge the message so it's not processed again
            r.xack(stream_name, group_name, message_id)

    except Exception as e:
        print(f"Entity Agent: An error occurred: {e}")
        # Sleep for a bit before retrying to avoid spamming errors
        time.sleep(5)