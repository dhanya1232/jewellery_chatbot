# Multimodal Jewellery Chatbot

A full-stack multimodal chatbot for jewellery use-cases:
- **Text ➜ Text**: Jewellery assistant chat
- **Image ➜ Text**: Describe jewellery photos
- **Text ➜ Image**: Generate jewellery concept images

## Stack
- **Frontend**: Chatbot-style UI with vanilla HTML/CSS/JS
- **Backend**: FastAPI
- **AI provider**: **Hugging Face Inference API** (free-tier friendly alternative)

> The app still works without tokens using deterministic fallback responses.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set HUGGINGFACE_API_TOKEN in .env for live generation
```

## Run

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000`

## API endpoints
- `POST /api/chat`
- `POST /api/image-to-text`
- `POST /api/text-to-image`

## Troubleshooting
- If the page looks plain/unstyled or chat doesn't answer, you are likely opening HTML directly or from a different server.
- Always run FastAPI and open `http://localhost:8000` so the UI can reach `/api/*` and static assets correctly.
