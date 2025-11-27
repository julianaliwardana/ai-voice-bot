# Real-time AI Voice Bot MVP

This is a Minimum Viable Product (MVP) for a real-time AI voice bot using:
- **AssemblyAI** for Speech-to-Text (STT)
- **GeminiAI** for Intelligence (LLM)
- **Cartesia** for Text-to-Speech (TTS)

## Setup

1.  **Install Dependencies**:
    The system should have already installed the python dependencies. If not, run:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install PortAudio on your system if `pyaudio` fails to install or run. On Windows, `pip install pyaudio` usually works. If not, try installing it from a wheel or use a package manager like `choco install portaudio`.*

2.  **API Keys**:
    Rename `.env.example` to `.env` and fill in your API keys:
    - `ASSEMBLYAI_API_KEY`
    - `GEMINI_API_KEY`
    - `CARTESIA_API_KEY`

3.  **Run**:
    ```bash
    python main.py
    ```

## Usage
- The bot will start listening immediately.
- Speak into your microphone.
- The bot will transcribe your speech, generate a response, and speak it back to you.
- Press `Ctrl+C` to stop.

## Troubleshooting
- **Microphone issues**: Ensure your default microphone is set correctly in your OS sound settings.
- **Audio output issues**: Ensure your speakers are working.
- **API Errors**: Check your API keys in the `.env` file.
