import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingEvents,
    StreamingParameters,
    TurnEvent,
    StreamingError
)
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

def on_turn(client: StreamingClient, event: TurnEvent):
    if event.transcript:
        print(f"{event.transcript} (End of turn: {event.end_of_turn})")

def on_error(client: StreamingClient, error: StreamingError):
    print(f"Error: {error}")

def main():
    client = StreamingClient(
        StreamingClientOptions(
            api_key=API_KEY,
            api_host="streaming.assemblyai.com",
        )
    )

    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Error, on_error)

    print("Connecting...")
    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True,
        )
    )

    print("Streaming... (Press Ctrl+C to stop)")
    try:
        client.stream(
            aai.extras.MicrophoneStream(sample_rate=16000)
        )
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        client.disconnect(terminate=True)

if __name__ == "__main__":
    main()
