# Make.com Blueprint — YouTube → MVP

This blueprint outlines a Make.com scenario to orchestrate the pipeline using HTTP + OpenAI steps.

## Flow

1. Webhook: Receive `{ "youtube_url": string, "title?": string }`
2. HTTP: `POST /api/projects` with body above
3. OpenAI (Whisper): Transcribe audio (optional if captions available)
4. OpenAI (GPT): Analyze transcript → spec.json
5. HTTP: Upload spec.json → `POST /api/projects/{id}/artifacts`
6. HTTP: Generate prototype → `POST /api/generate-prototype` (with `project_id` and spec)
7. HTTP: Mark complete → `POST /api/projects/{id}/complete`

> Note: This repo ships with local/offline stubs for transcription and analysis so you can demo without external services. Replace those by calling your OpenAI modules here and uploading the results to the backend.

## Example HTTP Modules

- Create Project (Step 2)
```
POST {{BACKEND_URL}}/api/projects
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Demo MVP"
}
```

- Upload Spec (Step 5)
```
POST {{BACKEND_URL}}/api/projects/{{id}}/artifacts
Content-Type: multipart/form-data
file=@spec.json
```

- Generate Prototype (Step 6)
```
POST {{BACKEND_URL}}/api/generate-prototype
Content-Type: application/json

{
  "project_id": {{id}},
  "spec": { /* JSON spec from GPT */ }
}
```

- Mark Complete (Step 7)
```
POST {{BACKEND_URL}}/api/projects/{{id}}/complete
```

## Variables

- `BACKEND_URL` — default `http://localhost:8000`
- `OPENAI_API_KEY` — used in your Whisper/GPT modules (not required by this backend in stub mode)

