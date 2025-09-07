#the final web page is showing these lines except AI ML and al other things are same so i think there is some har coded code so 
import redis
import whisper
import json
import time
import os

# Connect to Redis (running from our docker-compose setup)
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("STT Agent: Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"STT Agent: Could not connect to Redis. Please ensure it is running. Error: {e}")
    exit()

# This is a 'blocking' operation, so it may take a moment the first time.
print("STT Agent: Loading transcription model (whisper base.en)...")
model = whisper.load_model("base.en")
print("STT Agent: Model loaded successfully.")

def process_audio_file(filepath: str, session_id: str):
    print(f"STT Agent: Transcribing '{filepath}' for session '{session_id}'...")
    
    try:
        result = model.transcribe(filepath)
        transcript = result["text"]

        message = {
            "agent_id": "stt_agent",
            "timestamp": time.time(),
            "session_id": session_id,
            "transcript": transcript,
            "sources": [filepath]
        }

        r.xadd("stt_stream", {"data": json.dumps(message)})
        print(f"STT Agent: Published transcript to 'stt_stream'.")
        print(f"Transcript: \"{transcript}\"")

    except FileNotFoundError:
        print(f"STT Agent: ERROR - The audio file was not found at '{filepath}'.")
    except Exception as e:
        print(f"STT Agent: An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("\n--- STT Agent Test Run ---")

    # Always resolve test.mp3 relative to this script's folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(base_dir, "test.mp3")

    sample_session_id = "session_12345"
    process_audio_file(sample_file, sample_session_id)

    print("--- STT Agent Test Run Finished ---\n")
