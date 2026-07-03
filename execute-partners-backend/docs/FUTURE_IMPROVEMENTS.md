# Future improvements

Things I'd tackle next if I continued working on ExCom AI.

---

## AI / Gemini

- Migrate from `google.generativeai` to the newer `google.genai` SDK
- Add retry/backoff for Gemini rate limits (hit this during free-tier testing)
- Model fallback (Flash → Pro) for long article generation
- Stream chat responses over SSE for better UX in the Execute AI modal

## Filter / Moderation

- Host the identity-hate model on a company Hugging Face org instead of a personal repo
- Align the image moderation response shape between Node and Filter
- Rate limiting and request size caps on `/filtercomment`
- Cache inference results for duplicate text

## Architecture

- Redis for AI session persistence instead of the in-memory `SESSIONS` dict
- Unified health check that verifies Mongo, Gemini, and model load status
- CI pipeline with Docker build and smoke tests on PR

## DevOps

- Render blueprint as code in this repo
- Staging environment separate from production
- Structured logging and error tracking (Sentry)

## Product

- Multilingual moderation and summarization
- Admin dashboard for moderation appeals
