# execute-partners-backend

This folder contains the **AI services** I built for Execute Partners' ExCom community platform.

## What's here

| Folder | Service |
|--------|---------|
| [`ai/`](ai/) | Unified Gemini API — chat, summarize, trending, title & article generation |
| [`filter/`](filter/) | PyTorch content moderation — toxicity + identity-hate detection |
| [`docs/`](docs/) | Architecture, API reference, integration notes |

## Live (production)

| | URL |
|---|---|
| Community app | [executepartners.com/community](https://www.executepartners.com/community) |
| AI API | [ep-ai-api.onrender.com/docs](https://ep-ai-api.onrender.com/docs) |
| Filter API | [ep-ai-filter.onrender.com/health](https://ep-ai-filter.onrender.com/health) |

## Run locally

```bash
cd execute-partners-backend
cp .env.example .env
# Add GOOGLE_API_KEY

docker compose up --build
```

- AI Swagger: http://localhost:8000/docs  
- Filter health: http://localhost:7860/health  

## Full overview

See the [repository README](../README.md) for architecture, live demo links, and background.
