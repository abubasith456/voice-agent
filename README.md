## Gocare Voice Assistant (LiveKit + Multi-Agent)

Real-time voice assistant using LiveKit (Python SDK), Deepgram STT/TTS, and OpenRouter LLM. Includes a simple state-machine multi-agent flow for greeting/auth/main.

### Prerequisites
- Python 3.11+
- LiveKit Cloud or self-hosted server credentials
- Deepgram API key
- OpenRouter API key

### Quick Start
1. Copy environment:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies (user-site if venv not available):
   ```bash
   pip install --user -r requirements.txt
   ```
3. Run the worker:
   ```bash
   python worker.py
   ```

The worker expects `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` to be set. You can connect this worker to a LiveKit room and it will greet and handle queries.

### Environment Variables
- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET
- DEEPGRAM_API_KEY
- OPENROUTER_API_KEY
- OPENROUTER_BASE_URL (default: https://openrouter.ai/api/v1)
- OPENROUTER_MODEL (default: openai/gpt-4o-mini)

### Security
- The assistant refuses to provide passwords/PINs/OTPs and logs attempts.
- Mobile verification is simulated for demo. Integrate with your auth service in `MultiAgentManager._verify_mobile`.