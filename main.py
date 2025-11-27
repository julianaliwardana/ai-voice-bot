import os
import asyncio
import threading
import assemblyai as aai
import google.generativeai as genai
from cartesia import Cartesia
import pyaudio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

if not all([ASSEMBLYAI_API_KEY, GEMINI_API_KEY, CARTESIA_API_KEY]):
    print("Error: Missing API keys. Please check your .env file.")
    exit(1)

aai.settings.api_key = ASSEMBLYAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingEvents,
    StreamingParameters,
    TurnEvent,
    StreamingError
)

class VoiceBot:
    def __init__(self, loop):
        self.loop = loop
        self.cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)
        
        self.voice_id = "6ccbfb76-1fc6-48f7-b71d-91ac6298247b" 
        self.model_id = "sonic-english"

        self.client = None
        self.is_listening = True
        self.stop_signal = asyncio.Event()
        self.processing_task = None
        self.microphone_stream = None
        self.stream_thread = None
        
        # Transcript handling
        self.last_transcript = ""
        self.is_processing = False  # Prevent concurrent processing
        
        # Initialize Gemini
        self.system_instruction = "You are a helpful consultant. Your goal is to help the user with their requests, such as writing essays or exploring topics. You determine what is needed and gather information until the task can be completed. Ask clarifying questions to understand the topic, scope, and tone before generating the final content."
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=self.system_instruction
        )
        self.chat = self.model.start_chat()

    def start_transcription(self):
        print("Starting transcription...")
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=ASSEMBLYAI_API_KEY,
                api_host="streaming.assemblyai.com",
            )
        )

        self.client.on(StreamingEvents.Turn, self.on_turn)
        self.client.on(StreamingEvents.Error, self.on_error)

        self.client.connect(
            StreamingParameters(
                sample_rate=16000,
                format_turns=True,
                # Key settings for proper end-of-turn detection
                end_of_turn_confidence_threshold=0.5,  # Higher = more confident user finished (0.0-1.0)
                min_end_of_turn_silence_when_confident=480,  # Min silence (ms) before end turn when confident
                max_turn_silence=1600,  # Max silence (ms) to wait before ending turn
            )
        )
        
        # Start microphone stream in a separate thread so it doesn't block the event loop
        self.microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.stream_thread = threading.Thread(
            target=self.client.stream,
            args=(self.microphone_stream,),
            daemon=True
        )
        self.stream_thread.start()


    def on_turn(self, client: StreamingClient, event: TurnEvent):
        if not event.transcript:
            return

        # If user starts speaking, stop the bot's audio output
        if not self.stop_signal.is_set():
            self.loop.call_soon_threadsafe(self.stop_signal.set)

        transcript_text = event.transcript.strip()
        
        if event.end_of_turn:
            # Skip if already processing
            if self.is_processing:
                return
                
            # Normalize for comparison (lowercase, no punctuation)
            normalized = transcript_text.lower().rstrip('.!?')
            
            # Skip if empty or same as last processed transcript
            if not transcript_text or normalized == self.last_transcript:
                return
            
            self.is_processing = True
            self.last_transcript = normalized
            
            # Print final transcript only once
            print(f"You: {transcript_text}")
            self.loop.call_soon_threadsafe(self.stop_signal.clear)
            
            # Process the complete turn
            self.processing_task = asyncio.run_coroutine_threadsafe(
                self.process_turn(transcript_text), self.loop
            )

    def on_error(self, client: StreamingClient, error: StreamingError):
        print(f"An error occurred: {error}")

    async def process_turn(self, user_text):
        try:
            print("Bot: Thinking...", flush=True)
            response_text = await asyncio.wait_for(
                self.generate_response(user_text),
                timeout=10.0  # 30 second timeout
            )
            if response_text:
                print(f"Bot: {response_text}")
                await self.speak_response(response_text)
            else:
                print("Bot: [No response generated]")
        except asyncio.TimeoutError:
            print("Bot: [Response timed out]")
        except asyncio.CancelledError:
            print("[Task Cancelled]")
        except Exception as e:
            print(f"Error processing turn: {type(e).__name__}: {e}")
        finally:
            # Reset for next turn
            self.is_processing = False
            self.last_transcript = ""

    async def generate_response(self, text):
        try:
            response = await self.chat.send_message_async(text)
            return response.text
        except Exception as e:
            print(f"Error generating response: {type(e).__name__}: {e}")
            return f"Sorry, I had an error: {e}"

    async def speak_response(self, text):
        await self.loop.run_in_executor(None, self._speak_response_sync, text)

    def _speak_response_sync(self, text):
        try:
            ws = self.cartesia_client.tts.websocket()
            output = ws.send(
                model_id=self.model_id,
                transcript=text,
                voice={
                    "mode": "id",
                    "id": self.voice_id
                },
                stream=True,
                output_format={
                    "container": "raw",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                }
            )

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=44100,
                            output=True)

            for chunk in output:
                if self.stop_signal.is_set():
                    print("\n[Interrupted]")
                    break
                if hasattr(chunk, 'audio'):
                    stream.write(chunk.audio)

            stream.stop_stream()
            stream.close()
            p.terminate()
            ws.close()

        except Exception as e:
            print(f"Error speaking response: {e}")

    def stop(self):
        if self.client:
            self.client.disconnect(terminate=True)

if __name__ == "__main__":
    # Create a new event loop for async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot = VoiceBot(loop)
    
    try:
        bot.start_transcription()
        # Keep the main thread alive
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping...")
        bot.stop()
        loop.close()
