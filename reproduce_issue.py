import asyncio
import time
from unittest.mock import MagicMock

# Mock classes
class MockEvent:
    def __init__(self, transcript, end_of_turn):
        self.transcript = transcript
        self.end_of_turn = end_of_turn

class VoiceBot:
    def __init__(self, loop):
        self.loop = loop
        self.processing_task = None
        self.stop_signal = asyncio.Event()

    def on_turn(self, transcript, end_of_turn):
        print(f"User: {transcript} (Final: {end_of_turn})")
        
        if end_of_turn:
            print(f"Processing turn: {transcript}")
            self.loop.call_soon_threadsafe(self.stop_signal.clear)
            
            if self.processing_task and not self.processing_task.done():
                print("Canceling existing task...")
                self.processing_task.cancel()
            
            self.processing_task = asyncio.run_coroutine_threadsafe(self.process_turn(transcript), self.loop)

    async def process_turn(self, user_text):
        try:
            print(f"Thinking for '{user_text}'...")
            # Simulate processing time
            await asyncio.sleep(1) 
            print(f"Bot: Response to '{user_text}'")
        except asyncio.CancelledError:
            print(f"[Task Cancelled for '{user_text}']")
        except Exception as e:
            print(f"Error processing turn: {e}")

async def main():
    loop = asyncio.get_running_loop()
    bot = VoiceBot(loop)

    # Simulate rapid turns
    print("--- Simulating rapid turns ---")
    bot.on_turn("This", True)
    await asyncio.sleep(0.1)
    bot.on_turn("is", True)
    await asyncio.sleep(0.1)
    bot.on_turn("a", True)
    await asyncio.sleep(0.1)
    bot.on_turn("test", True)

    # Wait for tasks to complete
    await asyncio.sleep(2)

if __name__ == "__main__":
    # We need to run the bot's loop in a separate thread to match the real scenario?
    # In the real scenario, the loop is in the main thread, and on_turn is called from a background thread.
    # But run_coroutine_threadsafe is used to submit to the loop.
    
    # Here we can run the loop in the main thread and call on_turn from the main thread.
    # But run_coroutine_threadsafe requires a separate thread usually?
    # "This function is intended to be called from a different OS thread than the one where the event loop is running."
    # If called from the same thread, it might hang if the loop is blocked?
    # But here the loop is running.
    
    # Let's try to mimic the threading structure.
    import threading
    
    loop = asyncio.new_event_loop()
    
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()
        
    t = threading.Thread(target=run_loop)
    t.start()
    
    bot = VoiceBot(loop)
    
    print("--- Simulating rapid turns from main thread ---")
    bot.on_turn("This", True)
    time.sleep(0.2)
    bot.on_turn("is", True)
    time.sleep(0.2)
    bot.on_turn("a", True)
    time.sleep(0.2)
    bot.on_turn("test", True)
    
    time.sleep(3)
    loop.call_soon_threadsafe(loop.stop)
    t.join()
