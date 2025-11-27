import os
import asyncio
from cartesia import Cartesia
from dotenv import load_dotenv

load_dotenv()

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

async def debug_tts():
    client = Cartesia(api_key=CARTESIA_API_KEY)
    voice_id = "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"
    model_id = "sonic-english"
    
    print("Connecting to Cartesia...")
    ws = client.tts.websocket()
    
    print("Sending request...")
    output = ws.send(
        model_id=model_id,
        transcript="Hello, this is a test.",
        voice={
            "mode": "id",
            "id": voice_id
        },
        stream=True,
        output_format={
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100
        }
    )
    
    print(f"Output type: {type(output)}")
    
    try:
        for i, chunk in enumerate(output):
            print(f"Chunk {i} type: {type(chunk)}")
            print(f"Chunk attributes: {dir(chunk)}")
            if hasattr(chunk, 'audio'):
                print("Chunk has 'audio' attribute.")
            else:
                print("Chunk does NOT have 'audio' attribute.")
            break 
    except Exception as e:
        print(f"Error iterating output: {e}")

    ws.close()

if __name__ == "__main__":
    asyncio.run(debug_tts())
