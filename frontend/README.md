# Frontend — Next.js (YouTube → MVP)

This Next.js (App Router, TypeScript) frontend lets users paste a YouTube URL, view project dashboards, and download generated artifacts.

## Quickstart

```
npm install
npm run dev
```

Set `NEXT_PUBLIC_BACKEND_URL` (defaults to `http://localhost:8000`).

## Routes

- `/` — Landing page with form
- `/dashboard` — Lists projects from backend
- `/project/[id]` — Project detail with artifacts
- `/pricing` — Static pricing page

