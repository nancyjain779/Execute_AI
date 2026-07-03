# API Reference

Production base URLs for the services I built:

| Service | Production | Local |
|---------|------------|-------|
| AI API | `https://ep-ai-api.onrender.com` | `http://localhost:8000` |
| Filter API | `https://ep-ai-filter.onrender.com` | `http://localhost:7860` |
| Node API | `https://ep-node-api.onrender.com` | `http://localhost:5000` |

Interactive docs: [ep-ai-api.onrender.com/docs](https://ep-ai-api.onrender.com/docs)

Integration overview: [INTEGRATION.md](./INTEGRATION.md)

---

## Node API (Express + MongoDB)

Prefix: `{VITE_API_URL}/api/v1`

### `GET /health`

**Response:** `{ "status": "ok", "service": "node-api" }`

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Register user |
| POST | `/auth/signin` | Login → JWT |
| GET | `/auth/google` | Google OAuth (optional) |

### Articles & community

| Method | Path | Description |
|--------|------|-------------|
| GET | `/articles` | Community feed |
| POST | `/articles` | Create article (**filter moderated**) |
| POST | `/articles/:id/comments` | Add comment (**filter moderated**) |
| POST | `/articles/:id/like` | Like article |

**Moderation:** Node calls `FILTER_API_URL/filtercomment` via `node/services/filterService.js` before saving UGC.

### Chat

| Method | Path | Description |
|--------|------|-------------|
| GET | `/chat/:userId` | Chat history |

Real-time messages use **Socket.io** on the Node server (`register`, `send_message`, `mark_read` events).

---

## AI API (FastAPI + Gemini)

### `GET /health`

Health check.

**Response:** `{ "status": "ok" }`

---

### `GET /`

Service info.

**Response:** `{ "message": "Execute Partners Unified AI API" }`

---

### `GET /trending`

Returns top community articles by engagement score.

**Query params (optional):**

| Param | Default | Description |
|-------|---------|-------------|
| `weight_likes` | 1 | Like weight |
| `weight_comments` | 2 | Comment weight |
| `weight_shares` | 3 | Share weight |
| `top_n` | 5 | Number of results |

**Response:**

```json
{
  "trending": [
    {
      "title": "Article title",
      "slug": "article-slug",
      "engagement_score": 720,
      "likes": 1,
      "comments": 5,
      "shares": 7,
      "views": 172
    }
  ]
}
```

**Requires:** MongoDB with published articles.

---

### `POST /chat`

Community AI assistant (article Q&A, writing workflow).

**Body:**

```json
{
  "session_id": "user-or-session-id",
  "message": "Summarize this article",
  "text": "optional article context"
}
```

**Response:**

```json
{
  "session_id": "user-or-session-id",
  "response": "Assistant reply text"
}
```

---

### `POST /summarize`

Summarize an article or comment (Gemini + MongoDB persistence).

**Body:**

```json
{
  "article_id": "mongodb-object-id",
  "comment_id": "optional-comment-id",
  "delete": false
}
```

**Response:** Summary fields (`article_summary`, `comment_summary`, etc.)

---

### `POST /generate_title`

Generate article title suggestions for a category.

**Body:**

```json
{
  "category": "Business Transformation"
}
```

**Response:**

```json
{
  "title": { "text": "Generated title..." }
}
```

---

### `POST /generate_article`

Multi-turn article writing assistant.

**Body:**

```json
{
  "session_id": "session-id",
  "message": "Write about digital banking"
}
```

**Response:**

```json
{
  "response": "Assistant reply..."
}
```

---

### `POST /post_article`

Finalize and persist generated article content.

---

## Filter API (Flask + PyTorch + Gemini)

### `GET /health`

**Response:** `{ "status": "ok" }`

---

### `POST /filtercomment`

Moderate text, images, or article content.

**Form fields:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Text to moderate |
| `image_url` | string | Optional image URL |
| `image_file` | file | Optional upload |
| `article` | string | `"true"` for article classifier mode |

**Response (text):**

```json
{
  "safe": true,
  "toxic": 0.001,
  "identity_hate_custom": 0.01,
  "extracted_text": "hello"
}
```

**Models:** `unitary/toxic-bert` + identity-hate detector.

---

## Environment variables

See root `.env.example` and service README files.
