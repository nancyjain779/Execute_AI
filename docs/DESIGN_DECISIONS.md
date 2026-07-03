# Design decisions

Notes on the main architectural choices I made while building ExCom AI.

---

## Consolidating six microservices into one AI API

When I took over, chat, summarize, trending, title generation, and article generation each ran as a separate Render service — some duplicated, all with their own deploy configs.

I merged them into a single FastAPI application sharing Gemini config, prompts, and a MongoDB connection. One deploy, one CORS policy, shared session state for the article-writing workflow. This cut AI infrastructure costs by roughly 70%.

---

## Keeping the filter as a separate Docker service

I considered merging moderation into the FastAPI app but kept it separate because:

- PyTorch + transformers need ~2 GB RAM (Render Standard plan)
- The AI API stays lightweight — just Gemini HTTP calls
- Filter can restart or scale without affecting chat latency
- Models load once at container start and stay warm

---

## Gemini for language, BERT for classification

| Task | What I used |
|------|-------------|
| Chat, summarize, titles, articles | Google Gemini 2.0 Flash |
| Toxicity / identity-hate scoring | Fine-tuned BERT (local inference) |
| Image OCR | Gemini + local pipeline |

LLMs are great at generation; small classifiers are faster and cheaper for binary moderation scores. I didn't want to rely on Gemini alone for content safety.

---

## Direct browser → AI calls

I moved the frontend from hardcoded Render URLs to env-based config (`VITE_AI_API_URL`). The browser calls my AI API directly rather than proxying through Node.

Reasons: lower latency for chat and summarization, independent scaling, and simpler debugging — I can check AI logs without tracing through Node.

Moderation is the exception: that always goes Node → Filter, never client-side.

---

## Bundled model weights

I bundle `toxic-bert` and `identity-hate-detector` weights in the Docker image (~837 MB) so deploys don't depend on Hugging Face being available at runtime. Production uses the same approach with Git LFS.

---

## MongoDB for trending and context

Trending reads published articles from MongoDB and scores them by engagement. Summarize pulls article content from the same database. Chat and title generation can work with lighter Mongo dependency, but sharing the connection kept the architecture simple.

---

## What's intentionally not in this repo

The Node CMS backend and React marketing site are separate codebases owned by the wider team. I link to their production URLs in the README so reviewers can see the full system without me publishing code I didn't write.

Production secrets, admin routes, and internal tooling are also excluded.
