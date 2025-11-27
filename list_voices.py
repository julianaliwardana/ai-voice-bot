from cartesia import Cartesia
import os
from dotenv import load_dotenv

load_dotenv()

client = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))

try:
    voices = client.voices.list()
    try:
        first_voice = next(iter(voices))
        print(f"VOICE_ID:{first_voice.id}")
    except StopIteration:
        print("No voices found.")
except Exception as e:
    print(f"Error listing voices: {e}")
