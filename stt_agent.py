# stt_agent.py (Simplified Version - No Audio File Needed)

import redis
import json
import time

# Connect to Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("STT Agent (SIMULATED): Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"STT Agent (SIMULATED): Could not connect to Redis. Error: {e}")
    exit()

def simulate_transcription(session_id: str):
    """
    This function skips the audio file and transcription entirely.
    It creates a hardcoded transcript and publishes it.
    """
    print("STT Agent (SIMULATED): Generating a test transcript...")
    
    # This is the text we will pretend came from the audio file.
    # You can change the company names here to test different scenarios.
    transcript = "Our company is looking to improve our services, and we are evaluating Microsoft and also looking at Google's offerings."
    
    # Create the same message structure as before
    message = {
        "agent_id": "stt_agent_simulated",
        "timestamp": time.time(),
        "session_id": session_id,
        "transcript": transcript,
        "sources": ["simulated_audio"]
    }
    
    # Publish the 'utterance' event to the message bus
    r.xadd("stt_stream", {"data": json.dumps(message)})
    print(f"STT Agent (SIMULATED): Published transcript to 'stt_stream'.")
    print(f"Transcript: \"{transcript}\"")

if __name__ == "__main__":
    print("\n--- STT Agent Simulated Test Run ---")
    sample_session_id = "session_12345"
    
    # We now call the simulation function
    simulate_transcription(sample_session_id)
    
    print("--- STT Agent Test Run Finished ---\n")