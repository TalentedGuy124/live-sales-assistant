# ui_agent.py (v2 - More Robust Redis Listener)

import redis
import json
import asyncio
import websockets

# --- WebSocket Server ---
connected_clients = set()

async def handler(websocket):
    print(f"UI Agent: New browser client connected.")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("UI Agent: Browser client disconnected.")

async def start_websocket_server():
    async with websockets.serve(handler, "localhost", 8765):
        print("UI Agent: WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

# --- Redis Listener (Updated to be more robust) ---
async def redis_listener():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("UI Agent: Successfully connected to Redis.")
    except Exception as e:
        print(f"UI Agent: Could not connect to Redis. Error: {e}")
        return

    stream_name = "ranked_suggestion_stream"
    group_name = "ui_group"
    consumer_name = "ui_consumer_1"

    # Create the consumer group, similar to our other agents
    try:
        r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
        print(f"UI Agent: Consumer group '{group_name}' created.")
    except redis.exceptions.ResponseError:
        print(f"UI Agent: Consumer group '{group_name}' already exists.")

    print(f"UI Agent: Listening for suggestions on '{stream_name}'...")
    while True:
        try:
            # Use XREADGROUP to reliably read from the stream
            messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=1000)
            
            if messages:
                message_id, message_data = messages[0][1][0]
                data = message_data["data"]
                
                if connected_clients:
                    print(f"UI Agent: Forwarding suggestion to {len(connected_clients)} client(s).")
                    await websockets.broadcast(connected_clients, data)
                
                # Acknowledge the message so it isn't processed again
                r.xack(stream_name, group_name, message_id)
        except Exception as e:
            print(f"UI Agent: Error while listening to Redis: {e}")
        
        await asyncio.sleep(0.1)


# --- Main startup ---
async def main():
    websocket_task = asyncio.create_task(start_websocket_server())
    redis_task = asyncio.create_task(redis_listener())
    await asyncio.gather(websocket_task, redis_task)

if __name__ == "__main__":
    print("--- UI Agent Starting ---")
    asyncio.run(main())