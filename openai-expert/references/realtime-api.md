# Realtime API

Low-latency, continuous speech-to-speech API. Enables voice agent applications with bidirectional audio streaming.

## What It Does

- Native speech-to-speech (audio in → audio out, no STT/TTS roundtrip)
- Also supports text, image, and audio inputs/outputs
- Bidirectional audio streaming
- Phrase endpointing / turn detection (knows when user finishes speaking)
- User interrupt handling (user can cut off model mid-response)
- Conversation state management on the server

---

## Connection Methods

### WebRTC (Recommended for browser/mobile)

```javascript
// 1. Get ephemeral key from your server
const response = await fetch('/session');
const { client_secret } = await response.json();

// 2. Connect to Realtime model via WebRTC
const pc = new RTCPeerConnection();

// Add microphone audio track
const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
pc.addTrack(ms.getTracks()[0]);

// Handle model audio output
const audioEl = document.createElement('audio');
audioEl.autoplay = true;
pc.ontrack = (e) => { audioEl.srcObject = e.streams[0]; };

// Create data channel for events
const dc = pc.createDataChannel('oai-events');

// Create and send SDP offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

const sdpResponse = await fetch(
  'https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview',
  {
    method: 'POST',
    body: offer.sdp,
    headers: {
      'Authorization': `Bearer ${client_secret.value}`,
      'Content-Type': 'application/sdp'
    }
  }
);

const answer = { type: 'answer', sdp: await sdpResponse.text() };
await pc.setRemoteDescription(answer);
```

Advantages: Browser-native API, no granular audio event handling required, lower complexity.

### WebSocket (Recommended for server-to-server)

```python
import websockets
import json

async with websockets.connect(
    "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
    extra_headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "realtime=v1"}
) as ws:
    # Send session config
    await ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "instructions": "You are a helpful voice assistant.",
            "voice": "alloy",
            "turn_detection": {"type": "server_vad"}
        }
    }))
    
    # Send audio chunks
    await ws.send(json.dumps({
        "type": "input_audio_buffer.append",
        "audio": "<base64_encoded_pcm16>"
    }))
    
    # Or commit the buffer to trigger a response
    await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
    
    # Receive events
    async for message in ws:
        event = json.loads(message)
        if event["type"] == "response.audio.delta":
            # Stream audio bytes to output
            ...
```

Advantages: More granular control over audio events, better for server-side processing.

### SIP
Also supported for telephony integrations.

---

## Session Configuration

Key session parameters:
```json
{
  "modalities": ["text", "audio"],
  "instructions": "System prompt for the voice assistant",
  "voice": "alloy",
  "input_audio_format": "pcm16",
  "output_audio_format": "pcm16",
  "turn_detection": {
    "type": "server_vad",
    "threshold": 0.5,
    "prefix_padding_ms": 300,
    "silence_duration_ms": 500
  },
  "tools": [...],
  "temperature": 0.8
}
```

**Available voices:** alloy, ash, ballad, coral, echo, sage, shimmer, verse

**Audio formats:** pcm16 (raw), g711_ulaw, g711_alaw

---

## Key Events (WebSocket)

**Client → Server:**
- `session.update` — update session config
- `input_audio_buffer.append` — send audio data
- `input_audio_buffer.commit` — finalize audio input
- `input_audio_buffer.clear` — discard audio buffer
- `conversation.item.create` — inject message
- `response.create` — manually trigger response
- `response.cancel` — cancel in-progress response

**Server → Client:**
- `session.created`, `session.updated`
- `input_audio_buffer.speech_started`, `speech_stopped`
- `conversation.item.created`
- `response.created`, `response.done`
- `response.audio.delta` — audio chunk (base64 PCM)
- `response.audio_transcript.delta` — transcript of model speech
- `response.text.delta` — text output chunk
- `error`

---

## Ephemeral Keys

For browser WebRTC connections, generate a short-lived token server-side:
```
POST /v1/realtime/sessions
{
  "model": "gpt-4o-realtime-preview",
  "voice": "alloy"
}
```
Returns `client_secret.value` — a temporary key that expires quickly. Never expose your main API key in browser code.

---

## Use Cases

- **Voice agents** — customer support, virtual assistants
- **Real-time transcription + response** — meeting assistants
- **Phone bots** — via SIP integration
- **Accessibility tools** — voice interfaces for applications
- **Gaming** — real-time NPC voice interaction
